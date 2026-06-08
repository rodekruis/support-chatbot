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

