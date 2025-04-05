from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.air_quality import AirQualityData, AirQualityAnomaly
from app.services.database import db
from app.services.rabbitmq import rabbitmq
import json

router = APIRouter()

# Bu dosya, API endpoint'lerini organize etmek için kullanılacak
# Şu an sadece temel yapı oluşturuluyor, ileride farklı router'lar eklenebilir:
# - data_router.py (veri girişi ve sorgulamaları için)
# - anomaly_router.py (anomali sorgulamaları için)
# - map_router.py (harita görselleştirmesi için) 

@router.post("/data", status_code=201, response_model=dict)
async def add_air_quality_data(data: AirQualityData):
    """
    Yeni hava kalitesi verisi ekler ve RabbitMQ'ya mesaj gönderir.
    """
    # Veriyi MongoDB dokümanına dönüştür
    mongo_doc = data.to_mongo_document()
    
    # RabbitMQ'ya gönder
    await rabbitmq.publish("data.raw", mongo_doc)
    
    return {"status": "success", "message": "Veri başarıyla kuyruğa eklendi."}

@router.get("/air-quality/{latitude}/{longitude}", response_model=List[dict])
async def get_air_quality_by_location(
    latitude: float, 
    longitude: float,
    radius: float = Query(10.0, description="Arama yarıçapı (km)"),
    start_time: Optional[datetime] = Query(None, description="Başlangıç zamanı"),
    end_time: Optional[datetime] = Query(None, description="Bitiş zamanı"),
    limit: int = Query(100, description="Maksimum sonuç sayısı")
):
    """
    Belirli bir konuma yakın hava kalitesi verilerini getirir.
    """
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=1)
    if not end_time:
        end_time = datetime.utcnow()
    
    # Konum sorgusu oluştur (MongoDB $geoNear)
    geo_query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius * 1000  # metre cinsinden
            }
        },
        "timestamp": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    
    # Veritabanından verileri getir
    results = await db.get_air_quality_data(geo_query, limit)
    return results

@router.get("/anomalies", response_model=List[dict])
async def get_anomalies(
    start_time: Optional[datetime] = Query(None, description="Başlangıç zamanı"),
    end_time: Optional[datetime] = Query(None, description="Bitiş zamanı"),
    parameter: Optional[str] = Query(None, description="Filtre uygulanacak kirlilik parametresi"),
    limit: int = Query(100, description="Maksimum sonuç sayısı")
):
    """
    Belirli bir zaman aralığında tespit edilen anomalileri listeler.
    """
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=1)
    if not end_time:
        end_time = datetime.utcnow()
    
    # Sorgu oluştur
    query = {
        "detected_at": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    
    if parameter:
        query["parameter"] = parameter
    
    # Veritabanından anomalileri getir
    results = await db.get_anomalies(query, limit)
    return results

@router.get("/pollution-density", response_model=List[dict])
async def get_pollution_density(
    parameter: str = Query(..., description="Yoğunluğu görüntülenecek kirlilik parametresi"),
    start_time: Optional[datetime] = Query(None, description="Başlangıç zamanı"),
    end_time: Optional[datetime] = Query(None, description="Bitiş zamanı")
):
    """
    Coğrafi bölgeye göre kirlilik yoğunluğunu getirir.
    """
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=1)
    if not end_time:
        end_time = datetime.utcnow()
    
    # Aggregate sorgusu oluştur
    pipeline = [
        {
            "$match": {
                parameter: {"$exists": True},
                "timestamp": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "city": "$city",
                    "country": "$country"
                },
                "avg_value": {"$avg": f"${parameter}"},
                "max_value": {"$max": f"${parameter}"},
                "count": {"$sum": 1},
                "location": {"$first": "$location"}
            }
        },
        {
            "$sort": {"avg_value": -1}
        }
    ]
    
    # Veritabanından yoğunluk verilerini getir
    results = await db.aggregate_pollution_data(pipeline)
    return results 