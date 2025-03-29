from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_HOST, API_PORT

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