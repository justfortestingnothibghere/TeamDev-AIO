FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libgtk-3-0 libx11-xcb1 libxcomposite1 \
    libxcursor1 libxdamage1 libxfixes3 \
    libxi6 libxrandr2 libxrender1 libxss1 \
    libxtst6 libasound2 libdbus-glib-1-2 \
    libglib2.0-0 libnss3 libnspr4 \
    fonts-liberation libappindicator3-1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
