# The minor is pinned, not the patch: wud cannot watch this image (it is only ever a
# build input, see the labels on `web` in docker-compose.yml), so the patch releases
# have to arrive on their own -- `deploy.sh` pulls this tag at every deployment.
#
# 3.13 and not 3.14: the ceiling is Django, pinned to 5.1 in requirements.txt, which
# supports 3.10 to 3.13. Moving to 3.14 means moving Django first.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/db

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "drone_project.wsgi:application", "--bind", "0.0.0.0:8000", "--config", "gunicorn.conf.py"]
