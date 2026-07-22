# support-chatbot

Provides level-1 support for 510's products and services.
 
## Description

Synopsis: a [dockerized](https://www.docker.com/) [python](https://www.python.org/) API that serves a chatbot. Based on [langchain](https://github.com/langchain-ai/langchain) / [langgraph](https://github.com/langchain-ai/langgraph) and Azure OpenAI models. Uses [uv](https://docs.astral.sh/uv/) for dependency management.

## API Usage

See [the docs](https://support-chatbot.azurewebsites.net/docs).

### Configuration

```sh
cp example.env .env
```

Edit the provided [ENV-variables](./example.env) accordingly.

Read endpoints require `AUTH_API_KEY`. Write endpoints (for vector store refresh) require `AUTH_API_KEY_WRITE`.

### Manuals

The chatbot can serve multiple manuals (documentation sites). Each manual is
defined in [`manuals.yaml`](./src/support_chatbot/config/manuals.yaml) with the
URLs to scrape and chunking settings:

```yaml
manuals:
  "121":
    root_url: "https://manual.121.global/en/"
    base_url: "https://manual.121.global/en/"
    exclude_dirs:
      - "https://manual.121.global/en/nlrc"
    chunk_size: 1000
    chunk_overlap: 200
```

To add a manual: add an entry to `manuals.yaml`, create its prompt in Langfuse
(see [Prompts](#prompts)), then index it (see below).

Each manual is stored in its own search index named
`support-chatbot-index-{manual_id}` (e.g. `support-chatbot-index-121`). Non-prod
deployments append the environment name (e.g. `support-chatbot-index-121-dev`)
so that ingesting from dev never overwrites the prod index; set `ENVIRONMENT`
accordingly per deployment (`prod` keeps the bare name). Both `/ask`
and `/ingest-manual` require a `manual_id`:

- `POST /ask` — body `{"question": "...", "manual_id": "121"}`. Selects the
  manual's prompt, searches its index, and returns the answer with inline `[n]`
  citations and the backing `sources`. Optional body fields: `session_id`
  (groups a user's turns into one conversation/memory thread; a fresh id is
  generated per request when omitted, i.e. stateless) and `user_id` (attributed
  in Langfuse tracing).
- `POST /ask/stream` — same request body, but streams the answer as
  newline-delimited JSON (NDJSON): `{"type": "token", "text": ...}` fragments,
  a final `{"type": "done", "trace_id": ..., "sources": [...]}`, or
  `{"type": "error", "message": ...}` if generation fails mid-stream.
- `POST /ingest-manual?manual_id=121` — scrapes the manual and rebuilds
  its index.

> **Migration:** index naming changed from `support-chatbot-index` to
> `support-chatbot-index-{manual_id}`. Run `POST /ingest-manual?manual_id=121`
> once to populate the new index; the old index can then be deleted.

### Prompts

System prompts are loaded at runtime from [Langfuse](https://langfuse.com/)
prompt management (not from files), so they can be edited and versioned without
a redeploy. Langfuse credentials (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`,
`LANGFUSE_BASE_URL`) are therefore **required**. Two text prompts must exist:

- `citations` — product-agnostic; adds inline `[n]` citations to answers.
- `<manual_id>` — one per manual/product (e.g. `121`); used as that manual's
  system prompt. `POST /ask` fetches the prompt whose name equals the request's
  `manual_id`.

The prompt version fetched is selected by a Langfuse label derived from
`ENVIRONMENT`: `prod` maps to the `Production` label; other environments use
their own name (e.g. `dev`).

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
docker compose up --detach
```

### Run tests

```sh
uv run -- python -m pytest tests -v
```

