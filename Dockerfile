# ===========================================
# Stage 1: Build Node.js CLI (TypeScript)
# ===========================================
FROM node:18-alpine AS node-builder

WORKDIR /app

# Копируем package.json и зависимости
COPY package*.json ./
RUN npm ci

# Копируем исходный код и компилируем
COPY src/ ./src/
COPY tsconfig.json ./
RUN npm run build

# Устанавливаем только production зависимости в отдельной директории
RUN npm ci --omit=dev --prefix /app/prod

# ===========================================
# Stage 2: Production (Python + Node.js)
# ===========================================
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем Node.js runtime (без npm)
COPY --from=node:18-alpine /usr/local/bin/node /usr/local/bin/node
COPY --from=node:18-alpine /usr/lib /usr/lib

# Копируем скомпилированный imageFX CLI
RUN mkdir -p /app/imagefx
COPY --from=node-builder /app/dist /app/imagefx/dist
COPY --from=node-builder /app/package*.json /app/imagefx/
# Копируем production зависимости из builder
COPY --from=node-builder /app/prod/node_modules /app/imagefx/node_modules

# Возвращаемся в /app для FastAPI
WORKDIR /app

# Копируем Python зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем FastAPI приложение
COPY server/ ./server/

# Создаем non-root пользователя
RUN useradd -m -u 1001 apiuser && \
    chown -R apiuser:apiuser /app

# Переключаемся на non-root пользователя
USER apiuser

# Expose порт (по умолчанию 8080, настраивается через ENV)
EXPOSE 8080

# Переменные окружения (можно переопределить)
ENV API_HOST=0.0.0.0
ENV API_PORT=8080
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${API_PORT}/health')"

# Запуск FastAPI сервера
CMD ["sh", "-c", "uvicorn server.main:app --host ${API_HOST} --port ${API_PORT}"]
