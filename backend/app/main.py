from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from app.config import settings
from app.services.database import db
from app.services.rabbitmq import rabbitmq
from app.services.worker import worker
from app.api.router import router as api_router
from app.api.websocket import websocket_router

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hava Kirliliği İzleme API",
    description="Dünya genelinde hava kirlilik verilerini toplayan, analiz eden ve görselleştiren platform API'si",
    version="0.1.0",
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Güvenlik için production'da spesifik origin'ler belirtilmeli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Uygulama başlatılıyor...")
    
    # MongoDB bağlantısı ve indekslerin oluşturulması
    db_connected = False
    for attempt in range(3):  # Mongodb için 3 deneme
        try:
            await db.init_db()
            logger.info("MongoDB bağlantısı kuruldu.")
            db_connected = True
            break
        except Exception as e:
            logger.error(f"MongoDB bağlantısı sırasında hata (deneme {attempt+1}/3): {str(e)}")
            if attempt < 2:  # 3 denemeden az ise
                wait_time = (attempt + 1) * 5  # Her seferinde artan bekleme süresi
                logger.info(f"MongoDB bağlantısı için {wait_time} saniye bekleniyor...")
                await asyncio.sleep(wait_time)
    
    if not db_connected:
        logger.error("MongoDB bağlantısı kurulamadı. API sınırlı işlevsellik ile çalışacak.")
    
    # MongoDB başarılı olduktan sonra RabbitMQ bağlantısı ve kuyrukların oluşturulması
    rmq_connected = False
    for attempt in range(3):  # RabbitMQ için 3 deneme
        try:
            await rabbitmq.connect()
            await rabbitmq.setup_queues()
            logger.info("RabbitMQ bağlantısı kuruldu ve kuyruklar oluşturuldu.")
            rmq_connected = True
            break
        except Exception as e:
            logger.error(f"RabbitMQ bağlantısı sırasında hata (deneme {attempt+1}/3): {str(e)}")
            if attempt < 2:  # 3 denemeden az ise
                wait_time = (attempt + 1) * 5  # Her seferinde artan bekleme süresi
                logger.info(f"RabbitMQ bağlantısı için {wait_time} saniye bekleniyor...")
                await asyncio.sleep(wait_time)
    
    if not rmq_connected:
        logger.error("RabbitMQ bağlantısı kurulamadı. Mesajlaşma özellikleri çalışmayacak.")
    
    # RabbitMQ bağlantısı kurulduktan sonra worker servisini başlat
    if rmq_connected:
        try:
            # Worker servisinin RabbitMQ'nun hazır olması için biraz bekletme
            await asyncio.sleep(2)
            await worker.start()
            logger.info("Worker servisi başlatıldı.")
        except Exception as e:
            logger.error(f"Worker servisi başlatılırken hata: {str(e)}")
    else:
        logger.warning("RabbitMQ bağlantısı olmadığı için Worker servisi başlatılamadı.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Uygulama kapatılıyor...")
    
    # Worker servisini durdur
    try:
        await worker.stop()
        logger.info("Worker servisi durduruldu.")
    except Exception as e:
        logger.error(f"Worker servisi durdurulurken hata: {str(e)}")
    
    # RabbitMQ bağlantısının kapatılması
    try:
        await rabbitmq.close()
        logger.info("RabbitMQ bağlantısı kapatıldı.")
    except Exception as e:
        logger.error(f"RabbitMQ bağlantısı kapatılırken hata: {str(e)}")

@app.get("/")
async def root():
    """Ana sayfa endpoint'i"""
    return {"message": "Hava Kirliliği İzleme API'sine Hoş Geldiniz"}


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    # Her iki hizmetin durumunu kontrol et
    mongo_status = "healthy" if db.client else "unhealthy"
    rabbitmq_status = "healthy" if rabbitmq.connection else "unhealthy"
    
    # Genel durum, her iki hizmet de sağlıklıysa sağlıklı
    overall_status = "healthy" if mongo_status == "healthy" and rabbitmq_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "mongodb": mongo_status,
            "rabbitmq": rabbitmq_status
        }
    }


# API router'ını ekle
app.include_router(api_router, prefix="/api")

# WebSocket router'ını ekle
app.include_router(websocket_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True) 