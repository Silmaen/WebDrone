FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/db

COPY nginx.conf /etc/nginx/sites-available/default

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "drone_project.wsgi:application", "--bind", "127.0.0.1:8000", "--config", "gunicorn.conf.py"]
