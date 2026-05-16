FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN printf '#!/bin/sh\nset -e\n\
if [ -f "backend/manage.py" ]; then\n\
  cd backend\n\
elif [ ! -f "manage.py" ]; then\n\
  django-admin startproject core .\n\
fi\n\
python manage.py migrate --noinput\n\
exec python manage.py runserver 0.0.0.0:8000\n' > /start.sh && chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
