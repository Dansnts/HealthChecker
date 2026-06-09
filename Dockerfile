  # Stage 1 : install deps
  FROM python:3.13-slim AS builder
  WORKDIR /app

  COPY requirements.txt .

  RUN pip install --no-cache-dir -r requirements.txt

  # Stage 2 : final image
  FROM python:3.13-slim
  WORKDIR /app

  COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
  COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
  COPY ./python/app /app/
  COPY ./config.yaml /app/

  RUN useradd -m user && chown -R user /app
  USER user
  EXPOSE 8080
  CMD ["python", "api.py"]
