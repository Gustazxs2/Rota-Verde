FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema para GeoDjango, PostGIS e PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libpq-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Código do projeto Django
COPY backend/ .

# Porta utilizada pelo Render
EXPOSE 10000

# Inicialização da aplicação
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"]
