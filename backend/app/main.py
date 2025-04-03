from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_HOST, API_PORT
from app.services.database import db
from app.services.rabbitmq import rabbitmq

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
    # MongoDB bağlantısı ve indekslerin oluşturulması
    await db.init_db()
    
    # RabbitMQ bağlantısı ve kuyrukların oluşturulması
    await rabbitmq.connect()
    await rabbitmq.setup_queues()

@app.on_event("shutdown")
async def shutdown_event():
    # RabbitMQ bağlantısının kapatılması
    await rabbitmq.close()

@app.get("/")
async def root():
    """Ana sayfa endpoint'i"""
    return {"message": "Hava Kirliliği İzleme API'sine Hoş Geldiniz"}


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    return {"status": "healthy"}


# API router'ları burada eklenecek
# from app.api.router import router as api_router
# app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True) 