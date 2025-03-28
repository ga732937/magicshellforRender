FROM python:3.11-slim

# 安裝 Chrome 和相依套件
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends

# 安裝 Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製專案檔案
COPY . .

# 安裝 Python 相依套件
RUN pip install --no-cache-dir -r requirements.txt

# 建立必要的目錄
RUN mkdir -p data logs

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2

# 啟動服務
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:$PORT"]