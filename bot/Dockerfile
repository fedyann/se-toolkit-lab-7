FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
COPY uv.lock* .
COPY . .

RUN uv sync --no-dev

CMD ["uv", "run", "bot.py"]