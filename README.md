# support-chatbot

Provides level-1 support for 510's products and services.
 
## Description

Synopsis: a [dockerized](https://www.docker.com/) [python](https://www.python.org/) API that serves a chatbot. Based on [langchain](https://github.com/langchain-ai/langchain) / [langgraph](https://github.com/langchain-ai/langgraph) and Azure OpenAI models. Observability and evaluations through [Langfuse](https://langfuse.com/). Uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Manuals

The chatbot can serve multiple manuals (documentation sites). Each manual is
defined in [`manuals.yaml`](./src/support_chatbot/config/manuals.yaml):

```yaml
manuals:
  "121":
    # Required: crawling settings.
    root_url: "https://manual.121.global/en/" 
    base_url: "https://manual.121.global/en/"
    exclude_dirs:
      - "https://manual.121.global/en/nlrc"
    # Optional: split pages into chunks; omit to keep one page = one document.
    chunk_size: 1000
    chunk_overlap: 200
    # Optional: drop navigation/header/footer text repeated across pages.
    strip_boilerplate: true
    boilerplate_threshold: 0.9
```

Settings:

- `root_url` (required): the **seed** page where crawling starts (the first URL
  fetched).
- `base_url` (required): the **scope boundary**: a page is crawled only if it
  shares `base_url`'s host and sits at or below its path. Usually identical to
  `root_url`; set it differently only when the entry point and allowed scope
  diverge (e.g. seed from a deep landing page while allowing a broader subtree).
- `exclude_dirs` (optional, default none): URL prefixes removed from an
  otherwise in-scope crawl.
- `chunk_size` / `chunk_overlap` (optional): split each page into overlapping
  chunks of at most `chunk_size` characters, with `chunk_overlap` characters
  shared between consecutive chunks to preserve context across boundaries. Omit
  both to index whole pages without splitting.
- `strip_boilerplate` (optional, default `true`): remove navigation, header,
  and footer text that repeats across pages before indexing.
- `boilerplate_threshold` (optional, default `0.9`): when `strip_boilerplate`
  is enabled, a line is treated as boilerplate once it appears in at least this
  fraction (`0`–`1`) of the crawled pages.

To add a manual: add an entry to `manuals.yaml`, create its prompt in Langfuse
(see [Prompts](#prompts)), then index it (see below).

Each manual is stored in its own search index named
`support-chatbot-index-{manual_id}` (e.g. `support-chatbot-index-121`). Non-prod
deployments append the environment name (e.g. `support-chatbot-index-121-dev`)
so that ingesting from dev never overwrites the prod index; set `ENVIRONMENT`
accordingly per deployment (`prod` keeps the bare name).

### Usage

- `POST /ask`: body `{"question": "...", "manual_id": "121"}`. Selects the
  manual's prompt, searches its index, and returns the answer with inline `[n]`
  citations and the backing `sources`. Optional body fields: `session_id`
  (groups a user's turns into one conversation/memory thread; a fresh id is
  generated per request when omitted, i.e. stateless) and `user_id` (attributed
  in Langfuse tracing).
- `POST /ask/stream`: same request body, but streams the answer as
  newline-delimited JSON (NDJSON): `{"type": "token", "text": ...}` fragments,
  a final `{"type": "done", "trace_id": ..., "sources": [...]}`, or
  `{"type": "error", "message": ...}` if generation fails mid-stream.
- `POST /ingest-manual?manual_id=121`: scrapes the manual and rebuilds
  its index.

### Prompts

System prompts are loaded at runtime from Langfuse
prompt management (not from files), so they can be edited and versioned without
a redeploy. Three text prompts must exist:

- `citations`: product-agnostic; adds inline `[n]` citations to answers.
- `direct-answer`: product-agnostic; steers conversational / off-topic turns
  that skip retrieval (greetings, small talk, out-of-scope requests). Appended
  to the manual's system prompt on the router's `direct` branch.
- `<manual_id>`: one per manual/product (e.g. `121`); used as that manual's
  system prompt.

Each `<manual_id>` prompt must use the section structure `# Role`, `# Scope`,
`# Answering`, `# Conversation`. The `direct` branch reuses the manual prompt
but appends `direct-answer`, which instructs the model to follow `# Role` /
`# Scope` / `# Conversation` and **ignore `# Answering`** (the document-grounding
rules, including the "no documents retrieved" canned reply, apply only when
context is present). Keep these exact headers across manuals, or the override
silently no-ops.

The prompt version fetched is selected by a Langfuse label derived from
`ENVIRONMENT`: `prod` maps to the `Production` label; other environments use
their own name (e.g. `dev`).

### Observability & evaluation

Every question first passes through a **router** step that decides whether it
needs the manual (`retrieve`) or is a greeting / small talk / off-topic message
(`direct`). Only the `retrieve` branch runs retrieval; `direct` turns answer
conversationally with no document lookup (saving latency, cost, and tokens).

On the `retrieve` branch a **contextualize** step rewrites the latest message
into a standalone question using recent history (history-aware retrieval), so a
follow-up like "are you sure?" becomes an explicit question. That standalone
query is used both for retrieval and for evaluation (see below); first turns skip
the rewrite. The answer itself is still generated from the full conversation.

When the Langfuse keys are set, each `/ask` and `/ask/stream` request is traced
as a Langfuse root span named **`chat-turn`** (one per request); the router,
contextualize, retrieval, and LLM steps nest underneath it. The root span
exposes:

- **input**: the user's latest message, verbatim (plain string).
- **output**: the final answer.
- **metadata.`retrieval_used`**: `true` when the router chose retrieval.
- **metadata.`retrieved_context`**: the numbered `[n] page_content` block
  exactly as fed to the model; present **only** when `retrieval_used` is `true`
  (so a faithfulness judge sees the same context the answer was grounded on).
- **metadata.`search_query`**: the history-aware standalone question used for
  retrieval; present only when `retrieval_used` is `true`.- **metadata.`conversation_history`**: the prior question/answer turns as a
  plain transcript (no retrieved context, current turn excluded) — recorded on
  **every** turn for user-facing judges such as a distress evaluator.
`retrieved_context` lives on the `chat-turn` span, not on the child `generate` /
`AzureChatOpenAI` observations. When configuring an observation-level evaluator
(e.g. Faithfulness or Context Relevance), target the `chat-turn` observation,
**filter on `metadata.retrieval_used = true`** (so the judge skips chitchat /
off-topic turns that never retrieved), and map:

- `{{context}}` → **Metadata**, JsonPath `$.retrieved_context`
- `{{answer}}` → **Output** (no JsonPath)
- `{{question}}` → **Metadata**, JsonPath `$.search_query` (the standalone
  question, **not** the raw span input, so multi-turn follow-ups are scored
  against a self-contained question)

Targeting `chat-turn` (rather than the LLM generation) also ensures the judge
runs once per answer instead of on every internal LLM call. Traces are tagged
with `manual:<manual_id>`, carry the request's `session_id`/`user_id`, and are
namespaced by the `ENVIRONMENT` value (filterable in the Langfuse UI).

### Configuration

```sh
cp example.env .env
```

Edit the provided [ENV-variables](./example.env) accordingly.

Read endpoints require `AUTH_API_KEY`. Write endpoints (for vector store refresh) require `AUTH_API_KEY_WRITE`.

#### Environment variables

**Required**:

| Variable | Description |
| --- | --- |
| `AUTH_API_KEY` | API key for read endpoints (`/ask`, `/ask/stream`, `/feedback`). |
| `AUTH_API_KEY_WRITE` | API key for write endpoints (`/ingest-manual`). |
| `VECTOR_STORE_ADDRESS` | Azure AI Search endpoint URL. |
| `VECTOR_STORE_PASSWORD` | Azure AI Search admin/query key. |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint. |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key. |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version. |
| `MODEL_CHAT` | Azure OpenAI chat **deployment** name (not the model name). |
| `MODEL_EMBEDDINGS` | Azure OpenAI embeddings **deployment** name. |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key. Required because system prompts are loaded from Langfuse (see [Prompts](#prompts)). |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key. Required for the same reason. |

**Optional**:

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `8000` | Port the API binds to. |
| `ENVIRONMENT` | `prod` | Deployment environment. Namespaces vector-store indexes, selects the Langfuse prompt label, and tags Langfuse traces. `prod` keeps bare index names / the `Production` label. |
| `RETRIEVAL_K` | `8` | Manual pages retrieved per question. Lower reduces latency/cost at the risk of missing context. |
| `CITATIONS_ENABLED` | `true` | Add inline `[n]` citations mapping answers to sources. |
| `MODEL_JUDGE` | _(none)_ | Evaluation-only: separate (stronger) deployment used as LLM-as-judge in offline RAG tests. Unset skips those tests. |
| `LANGFUSE_BASE_URL` | _(Langfuse cloud)_ | Base URL of a self-hosted Langfuse. Set only when not using Langfuse cloud. |

> Setting the Langfuse keys also enables LLM tracing (latency, token usage,
> user feedback) in addition to prompt loading.

### Run locally

First initialize the API
```sh
uv sync
uv run uvicorn main:app --reload
```

Then initialize the interface
```shell
uv run streamlit run interface/app.py
```

### Run with Docker

```sh
docker build -t support-chatbot .
docker run --env-file .env -p 8000:8000 support-chatbot
```

### Run tests

```sh
uv run -- python -m pytest tests -v
```

