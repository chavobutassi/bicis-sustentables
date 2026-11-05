FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /srv

COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

COPY app app
RUN useradd --system --no-create-home bicis
USER bicis

# Un solo proceso: el límite de intentos de acceso vive en memoria.
# --proxy-headers: detrás del proxy de la plataforma, toma la IP real del cliente.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
