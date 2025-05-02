FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY trading_bot.py .

# Crear directorio de logs
RUN mkdir -p /app/logs

# Instalar cron
RUN apt-get update && apt-get -y install cron

# Configurar cron job (6 AM hora de México)
RUN echo "0 6 * * * cd /app && python /app/trading_bot.py >> /app/logs/trading_bot.log 2>&1" > /etc/cron.d/trading-cron
RUN chmod 0644 /etc/cron.d/trading-cron
RUN crontab /etc/cron.d/trading-cron

# Script de inicio
RUN echo "#!/bin/sh\ncron -f" > /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
