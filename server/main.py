"""
FastAPI HTTP API для imageFX-api

Предоставляет REST endpoints для генерации изображений через Google ImageFX
"""
import os
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.models import (
    GenerateRequest, GenerateResponse, ImageData,
    FetchResponse,
    CaptionRequest, CaptionResponse,
    HealthResponse, ErrorResponse
)
from server.utils import run_imagefx_generate, run_imagefx_fetch, run_imagefx_caption, get_cookie


# Логирование
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI(
    title="imageFX API",
    description="HTTP API для генерации изображений через Google ImageFX (Imagen 3/4)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (разрешаем все origins для API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Корневой endpoint с информацией об API"""
    return {
        "name": "imageFX API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /generate",
            "fetch": "GET /fetch/{media_id}",
            "caption": "POST /caption",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint для мониторинга"""
    cookie_set = bool(os.getenv("GOOGLE_COOKIE"))
    
    return HealthResponse(
        status="ok",
        cookie_set=cookie_set
    )


@app.post(
    "/generate",
    response_model=GenerateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный запрос"},
        500: {"model": ErrorResponse, "description": "Ошибка генерации"}
    },
    tags=["Image Generation"]
)
async def generate_images(request: GenerateRequest):
    """
    Генерация изображений из текстового промпта
    
    - **prompt**: Описание изображения (обязательно)
    - **model**: Модель генерации (IMAGEN_3, IMAGEN_3_1, IMAGEN_3_5)
    - **aspect_ratio**: Соотношение сторон (SQUARE, PORTRAIT, LANDSCAPE)
    - **count**: Количество изображений (1-8)
    - **seed**: Seed для воспроизводимости (0+)
    
    Возвращает массив изображений в base64 формате
    """
    try:
        logger.info(f"Generate request: prompt='{request.prompt[:50]}...', model={request.model}, count={request.count}")
        
        # Вызываем CLI
        images_data = run_imagefx_generate(
            prompt=request.prompt,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            count=request.count,
            seed=request.seed
        )
        
        # Конвертируем в Pydantic модели
        images = [ImageData(**img) for img in images_data]
        
        logger.info(f"Generated {len(images)} images successfully")
        
        return GenerateResponse(
            images=images,
            count=len(images)
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error in generate endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get(
    "/fetch/{media_id}",
    response_model=FetchResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Изображение не найдено"},
        500: {"model": ErrorResponse, "description": "Ошибка получения"}
    },
    tags=["Image Retrieval"]
)
async def fetch_image(media_id: str):
    """
    Получение изображения по Media ID
    
    - **media_id**: Уникальный идентификатор изображения
    
    Возвращает изображение в base64 формате
    """
    try:
        logger.info(f"Fetch request: media_id={media_id}")
        
        image_data = run_imagefx_fetch(media_id)
        
        logger.info(f"Fetched image {media_id} successfully")
        
        return FetchResponse(**image_data)
        
    except RuntimeError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with media_id '{media_id}' not found"
            )
        logger.error(f"Fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error in fetch endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post(
    "/caption",
    response_model=CaptionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Неверный запрос"},
        500: {"model": ErrorResponse, "description": "Ошибка генерации описания"}
    },
    tags=["Image Analysis"]
)
async def generate_caption(request: CaptionRequest):
    """
    Генерация описания (caption) из изображения
    
    - **image_base64**: Изображение в base64 (data:image/TYPE;base64,...)
    - **image_type**: Тип изображения (PNG, JPEG, WEBP, etc.)
    - **count**: Количество вариантов описания (1-10)
    
    Возвращает массив текстовых описаний
    """
    try:
        logger.info(f"Caption request: image_type={request.image_type}, count={request.count}")
        
        captions = run_imagefx_caption(
            image_base64=request.image_base64,
            image_type=request.image_type,
            count=request.count
        )
        
        logger.info(f"Generated {len(captions)} captions successfully")
        
        return CaptionResponse(
            captions=captions,
            count=len(captions)
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Caption generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caption generation failed: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error in caption endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик всех необработанных исключений"""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        reload=False,  # Отключаем reload в production
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
