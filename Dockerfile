FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN python -m pip install uv

# Copy dependencies file and install dependencies
COPY pyproject.toml .
RUN uv pip install --system psycopg2-binary azure-storage-blob python-dotenv

COPY . .

CMD ["python", "main.py"]