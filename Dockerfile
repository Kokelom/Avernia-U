from python:3.12-slim

env PYTHONDONTWRITEBYTECODE=1
env PYTHONUNBUFFERED=1

workdir /code

run apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

copy pyproject.toml poetry.lock ./
run pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

copy app ./app
copy data/ ./data
copy tests ./tests/
expose 8000

cmd ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]