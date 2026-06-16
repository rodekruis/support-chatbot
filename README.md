# support-chatbot

Provides level-1 support for 510's products and services.
 
## Description

Synopsis: a [dockerized](https://www.docker.com/) [python](https://www.python.org/) API that serves a chatbot. Based on [langchain](https://github.com/langchain-ai/langchain) and OpenAI models. Uses [uv](https://docs.astral.sh/uv/) for dependency management.

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
URLs to scrape, chunking settings, and an optional per-manual system prompt:

```yaml
manuals:
  "121":
    root_url: "https://manual.121.global/en/"
    base_url: "https://manual.121.global/en/"
    exclude_dirs:
      - "https://manual.121.global/en/nlrc"
    chunk_size: 1000
    chunk_overlap: 200
    # Optional: a Markdown prompt relative to the support_chatbot package.
    # Falls back to prompts/support_chatbot_prompt.md when omitted.
    # prompt_file: "prompts/manual_121.md"
```

To add a manual: add an entry to `manuals.yaml`, optionally add a prompt
Markdown file under [`prompts/`](./src/support_chatbot/prompts/), then index it
(see below).

Each manual is stored in its own search index named
`{VECTOR_STORE_ID}-{manual_id}` (e.g. `support-chatbot-index-121`). Both `/ask`
and `/ingest-manual` require a `manual_id`:

- `POST /ask` — body `{"question": "...", "manual_id": "121"}`. Selects the
  manual's prompt and searches its index.
- `POST /ingest-manual?manual_id=121` — scrapes the manual and rebuilds
  its index.

> **Migration:** index naming changed from `{VECTOR_STORE_ID}` to
> `{VECTOR_STORE_ID}-{manual_id}`. Run `POST /ingest-manual?manual_id=121`
> once to populate the new index; the old index can then be deleted.

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
uv run pytest tests -v
```

