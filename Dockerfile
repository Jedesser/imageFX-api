# Stage 1: Builder
FROM node:18-alpine AS builder

WORKDIR /app

# Копируем package.json и package-lock.json для кеширования зависимостей
COPY package*.json ./

# Устанавливаем все зависимости (включая dev)
RUN npm ci

# Копируем исходный код
COPY . .

# Компилируем TypeScript
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Создаем non-root пользователя для безопасности
RUN addgroup -g 1001 -S imagefx && \
    adduser -u 1001 -S imagefx -G imagefx

# Копируем только необходимые файлы из builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist

# Устанавливаем только production зависимости
RUN npm ci --omit=dev && \
    npm cache clean --force

# Создаем директорию для вывода изображений
RUN mkdir -p /output && \
    chown -R imagefx:imagefx /app /output

# Переключаемся на non-root пользователя
USER imagefx

# Устанавливаем рабочую директорию для вывода
WORKDIR /output

# Указываем entrypoint для CLI
ENTRYPOINT ["node", "/app/dist/cli.js"]

# По умолчанию показываем help
CMD ["--help"]
