
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo '#!/bin/sh\n\
set -e\n\
if [ ! -f "manage.py" ]; then\n\
  django-admin startproject core .\n\
fi\n\
echo "--- URUCHAMIAM SERWER ---"\n\
exec python manage.py runserver 0.0.0.0:8000\n' > /start.sh && chmod +x /start.sh

ENTRYPOINT ["/start.sh"]