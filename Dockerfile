FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY ./python/app /app/
COPY ./config.yaml /app/

RUN useradd -m user && chown -R user /app
USER user

CMD ["python", "api.py"]
