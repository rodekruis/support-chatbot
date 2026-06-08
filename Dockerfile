# python base image in the container from Docker Hub
FROM python:3.12-slim

# copy files to the /app folder in the container
COPY ./src /app/src
COPY ./main.py /app/main.py
COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock

# install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# set the working directory in the container to be /app
WORKDIR /app

# install required packages in a local virtual environment
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"
RUN python -m spacy download en_core_web_sm

# expose the port that uvicorn will run the app on
ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# use gunicorn + uvicorn workers in production
CMD ["gunicorn", "support_chatbot.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
