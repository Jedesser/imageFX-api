#!/bin/bash

# imagefx.sh - Обертка для удобного использования imageFX-api в Docker

set -e

IMAGE_NAME="imagefx-api:latest"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Ошибка: Docker не установлен${NC}"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверка наличия GOOGLE_COOKIE
if [ -z "$GOOGLE_COOKIE" ]; then
    echo -e "${YELLOW}Предупреждение: переменная окружения GOOGLE_COOKIE не установлена${NC}"
    echo "Для работы необходимо установить cookie:"
    echo "  export GOOGLE_COOKIE=\"ваш_cookie_здесь\""
    echo ""
    echo -e "${YELLOW}Продолжаю без cookie (некоторые команды могут не работать)...${NC}"
    echo ""
fi

# Проверка наличия образа, если нет - собираем
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo -e "${YELLOW}Образ $IMAGE_NAME не найден. Начинаю сборку...${NC}"
    docker build -t "$IMAGE_NAME" "$(dirname "$0")"
    echo -e "${GREEN}Образ успешно собран!${NC}"
fi

# Создаем директорию для вывода, если не существует
mkdir -p "$OUTPUT_DIR"

# Запускаем контейнер с передачей всех аргументов
docker run --rm \
    -e GOOGLE_COOKIE="$GOOGLE_COOKIE" \
    -v "$(pwd)/$OUTPUT_DIR:/output" \
    -u "$(id -u):$(id -g)" \
    "$IMAGE_NAME" "$@"
