import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router as api_router
from app.api.websocket import router as websocket_router
from app.services.rabbitmq import rabbitmq
from app.services.worker import start_workers
from app.services.database import db
from app.utils.json_encoder import JSONEncoder
import json
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.encoders import jsonable_encoder
import asyncio

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="Hava Kirliliği İzleme API",
    description="Hava kirliliği verilerini toplayan ve analiz eden API.",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (geliştirme için)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ObjectId'leri string'e dönüştürmek için özel JSON serileştirme
@app.middleware("http")
async def custom_json_serializer(request: Request, call_next):
    response = await call_next(request)
    
    if response.headers.get("content-type") == "application/json":
        body = await response.body()
        try:
            # JSON'u decode et
            body_dict = json.loads(body)
            # ObjectId'leri string'e dönüştür
            json_compatible_body = json.dumps(body_dict, cls=JSONEncoder)
            # Yeni response oluştur
            return JSONResponse(
                content=json.loads(json_compatible_body),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )
        except:
            # Hata durumunda orijinal response döndür
            return response
    
    return response

# API router'ları
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(websocket_router, tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    # RabbitMQ bağlantısı
    await rabbitmq.connect()
    await rabbitmq.setup_exchanges_and_queues()
    logger.info("RabbitMQ bağlantısı kuruldu")
    
    # MongoDB bağlantısı
    await db.init_db()
    logger.info("MongoDB bağlantısı kuruldu")
    
    # Worker'ları başlat
    asyncio.create_task(start_workers())
    logger.info("Worker'lar başlatıldı")

@app.on_event("shutdown")
async def shutdown_event():
    # RabbitMQ bağlantısını kapat
    await rabbitmq.close()
    logger.info("RabbitMQ bağlantısı kapatıldı")

@app.get("/")
async def root():
    return {"message": "Hava Kirliliği İzleme API'ye Hoş Geldiniz"}

@app.get("/health")
async def health_check():
    # MongoDB ve RabbitMQ durumlarını kontrol et
    mongodb_status = "up" if db.db is not None else "down"
    rabbitmq_status = "up" if rabbitmq.connection is not None else "down"
    
    return {
        "status": "ok" if mongodb_status == "up" and rabbitmq_status == "up" else "error",
        "services": {
            "mongodb": mongodb_status,
            "rabbitmq": rabbitmq_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 