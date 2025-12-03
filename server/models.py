"""
Pydantic модели для FastAPI валидации запросов/ответов
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# Типы для констант
ModelType = Literal["IMAGEN_3", "IMAGEN_3_1", "IMAGEN_3_5"]
AspectRatioType = Literal[
    "IMAGE_ASPECT_RATIO_SQUARE",
    "IMAGE_ASPECT_RATIO_PORTRAIT", 
    "IMAGE_ASPECT_RATIO_LANDSCAPE",
    "IMAGE_ASPECT_RATIO_UNSPECIFIED"
]
ImageType = Literal["jpeg", "jpg", "jpe", "png", "gif", "webp", "svg", "bmp", "tiff", "apng", "avif"]


class GenerateRequest(BaseModel):
    """Запрос на генерацию изображений"""
    prompt: str = Field(..., description="Текстовое описание изображения", min_length=1)
    model: Optional[ModelType] = Field("IMAGEN_3", description="Модель генерации")
    aspect_ratio: Optional[AspectRatioType] = Field(
        "IMAGE_ASPECT_RATIO_LANDSCAPE", 
        description="Соотношение сторон"
    )
    count: Optional[int] = Field(1, description="Количество изображений", ge=1, le=8)
    seed: Optional[int] = Field(0, description="Seed для воспроизводимости", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Космический корабль в стиле sci-fi",
                "model": "IMAGEN_3_5",
                "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
                "count": 2,
                "seed": 42
            }
        }


class ImageData(BaseModel):
    """Данные одного изображения"""
    media_id: str = Field(..., description="Уникальный ID изображения")
    base64: str = Field(..., description="Изображение в base64 (data:image/png;base64,...)")
    prompt: str = Field(..., description="Использованный промпт")
    model: str = Field(..., description="Использованная модель")
    seed: int = Field(..., description="Использованный seed")
    aspect_ratio: str = Field(..., description="Соотношение сторон")


class GenerateResponse(BaseModel):
    """Ответ с сгенерированными изображениями"""
    images: List[ImageData] = Field(..., description="Массив сгенерированных изображений")
    count: int = Field(..., description="Количество изображений")


class FetchResponse(BaseModel):
    """Ответ с одним изображением по Media ID"""
    media_id: str
    base64: str
    prompt: str
    model: str
    seed: int
    aspect_ratio: str


class CaptionRequest(BaseModel):
    """Запрос на генерацию описания из изображения"""
    image_base64: str = Field(..., description="Изображение в base64 (data:image/TYPE;base64,...)")
    image_type: ImageType = Field("PNG", description="Тип изображения")
    count: Optional[int] = Field(1, description="Количество вариантов описания", ge=1, le=10)

    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
                "image_type": "png",
                "count": 3
            }
        }


class CaptionResponse(BaseModel):
    """Ответ с описаниями изображения"""
    captions: List[str] = Field(..., description="Массив описаний")
    count: int = Field(..., description="Количество описаний")


class HealthResponse(BaseModel):
    """Health check ответ"""
    status: str = Field("ok", description="Статус сервиса")
    cookie_set: bool = Field(..., description="Установлен ли GOOGLE_COOKIE")


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    detail: str = Field(..., description="Описание ошибки")
    error_code: Optional[str] = Field(None, description="Код ошибки")
