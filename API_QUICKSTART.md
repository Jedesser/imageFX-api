# FastAPI HTTP API для imageFX

## 🌐 Быстрый старт

### Запуск с Docker Compose

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/Jedesser/imageFX-api.git
cd imageFX-api

# 2. Создайте .env файл
echo "GOOGLE_COOKIE=ваш_cookie_здесь" > .env

# 3. Запустите API сервер
docker-compose up -d imagefx-api

# 4. API доступен на http://localhost:8080
curl http://localhost:8080/health
```

---

## 📡 API Endpoints

### 1. GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "cookie_set": true
}
```

### 2. POST `/generate`
Генерация изображений из промпта

**Request:**
```json
{
  "prompt": "Космический корабль в стиле sci-fi",
  "model": "IMAGEN_3_5",
  "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
  "count": 2,
  "seed": 42
}
```

**Response:**
```json
{
  "images": [
    {
      "media_id": "image-1733234567890",
      "base64": "data:image/png;base64,iVBORw0KGgo...",
      "prompt": "Космический корабль в стиле sci-fi",
      "model": "IMAGEN_3_5",
      "seed": 42,
      "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE"
    }
  ],
  "count": 2
}
```

### 3. GET `/fetch/{media_id}`
Получение изображения по Media ID

**Response:**
```json
{
  "media_id": "abc123",
  "base64": "data:image/png;base64,iVBORw0KGgo...",
  "prompt": "N/A",
  "model": "N/A",
  "seed": 0,
  "aspect_ratio": "N/A"
}
```

### 4. POST `/caption`
Генерация описания из изображения

**Request:**
```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo...",
  "image_type": "PNG",
  "count": 3
}
```

**Response:**
```json
{
  "captions": [
    "Описание изображения вариант 1",
    "Описание изображения вариант 2",
    "Описание изображения вариант 3"
  ],
  "count": 3
}
```

---

## 🔧 Примеры использования

### Curl

```bash
# Генерация изображения
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Футуристический город ночью",
    "model": "IMAGEN_3_5",
    "count": 1
  }'

# Health check
curl http://localhost:8080/health

# Получение по Media ID
curl http://localhost:8080/fetch/image-1733234567890
```

### Python

```python
import requests
import base64

# Генерация
response = requests.post("http://localhost:8080/generate", json={
    "prompt": "Космический корабль",
    "model": "IMAGEN_3_5",
    "count": 1
})

data = response.json()
image_base64 = data["images"][0]["base64"]

# Сохранение изображения
img_data = image_base64.split(",")[1]
with open("output.png", "wb") as f:
    f.write(base64.b64decode(img_data))
```

### JavaScript/TypeScript

```typescript
// Генерация
const response = await fetch("http://localhost:8080/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    prompt: "Космический корабль",
    model: "IMAGEN_3_5",
    count: 1
  })
});

const data = await response.json();
console.log(data.images[0].media_id);
```

---

## 🐳 Настройка Dockploy

### Domain Configuration

| Параметр | Значение |
|----------|----------|
| **Service Name** | imagefx-api |
| **Host** | imagefx-api.yourdomain.com |
| **Path** | / |
| **Internal Path** | / |
| **Strip Path** | ❌ Выключить |
| **Container Port** | **8080** |

### Environment Variables

Добавьте в Dockploy:

```bash
GOOGLE_COOKIE=ваш_полный_cookie_строка_из_labs.google
API_PORT=8080
LOG_LEVEL=INFO
```

---

## 📚 Swagger UI

Интерактивная документация доступна на:
- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc

---

## ⚙️ Кастомизация порта

Если порт 8080 занят, измените в `.env`:

```bash
API_PORT=1256  # Ваш свободный порт
```

И в `docker-compose.yml`:

```yaml
ports:
  - "1256:1256"  # Внешний:Внутренний
```

---

## 🔍 Логи и мониторинг

```bash
# Просмотр логов
docker-compose logs -f imagefx-api

# Health check
curl http://localhost:8080/health

# Метрики контейнера
docker stats imagefx-api
```

---

**Полная документация:** [RUSSIAN_GUIDE.md](file:///projects/imagefx-api/RUSSIAN_GUIDE.md)
