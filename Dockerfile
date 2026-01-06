FROM python:3.11-slim

# ---- system deps ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---- install deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- copy app ----
COPY app ./app
COPY pyrightconfig.json .
COPY pytest.ini .

# ---- security: non-root user ----
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# ---- run ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
