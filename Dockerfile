FROM astral/uv:python3.12-bookworm-slim
WORKDIR /usr/local/app

COPY pyproject.toml uv.lock ./
RUN uv sync

EXPOSE 8000

COPY . .

CMD [ "uv", "run", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]