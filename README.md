# support-chatbot

<img width="250" src="https://github.com/user-attachments/assets/faf65773-f731-44cb-a145-ea0f30cea58f" />

Chat with [121 user manual](https://manual.121.global). You can try it out at [support-chatbot.streamlit.app](https://support-chatbot.streamlit.app/).
 
## Description

Synopsis: a [dockerized](https://www.docker.com/) [python](https://www.python.org/) API to serve a chatbot for [121](https://github.com/global-121). Based on [langchain](https://github.com/langchain-ai/langchain) and OpenAI models. Uses [uv](https://docs.astral.sh/uv/) for dependency management.

## API Usage

See [the docs](https://hia-chatbot.azurewebsites.net/docs).

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

