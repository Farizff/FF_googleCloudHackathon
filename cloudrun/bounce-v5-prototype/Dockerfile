FROM python:3.12-slim

LABEL org.opencontainers.image.title="bounce-v5-prototype"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py ./app.py
COPY index.html ./index.html

EXPOSE 8080
CMD ["python", "app.py"]
