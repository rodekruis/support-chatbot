# python base image in the container from Docker Hub
FROM python:3.12-slim

# install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# set the working directory in the container to be /app
WORKDIR /app

# install dependencies first using only the lockfile so this layer is cached
# across code-only changes; a cache mount avoids re-downloading wheels
COPY ./pyproject.toml ./uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# copy the application source and install the project itself
COPY ./src /app/src
COPY ./main.py /app/main.py
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# expose the port that uvicorn will run the app on
ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# use gunicorn + uvicorn workers in production
CMD ["gunicorn", "support_chatbot.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
