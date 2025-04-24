from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.air_quality import AirQualityData, AirQualityAnomaly
from app.services.database import db
from app.services.rabbitmq import rabbitmq
from app.utils.json_encoder import convert_mongo_document, dump_json
import json
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

# Bu dosya, API endpoint'lerini organize etmek için kullanılacak
# Şu an sadece temel yapı oluşturuluyor, ileride farklı router'lar eklenebilir:
# - data_router.py (veri girişi ve sorgulamaları için)
# - anomaly_router.py (anomali sorgulamaları için)
# - map_router.py (harita görselleştirmesi için) 

@router.post("/data", status_code=201)
async def add_air_quality_data(data: AirQualityData):
    """
    Yeni hava kalitesi verisi ekler ve RabbitMQ'ya mesaj gönderir.
    """
    # Veriyi MongoDB dokümanına dönüştür
    mongo_doc = data.to_mongo_document()
    
    # RabbitMQ'ya gönder
    await rabbitmq.publish("data.raw", mongo_doc)
    
    return {"status": "success", "message": "Veri başarıyla kuyruğa eklendi."}

@router.get("/air-quality/{latitude}/{longitude}")
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
    try:
        # Basitleştirilmiş yaklaşım: sadece zamana göre filtrele
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Konum filtrelemeyi devre dışı bırak
        query = {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }
        
        # Veritabanından doğrudan veriler getir
        logging.info(f"Hava kalitesi verisi sorgulanıyor (manüel): tarih={start_time} - {end_time}")
        
        # MongoDB'den doğrudan sorgula
        collection = db.db.air_quality_data
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # ObjectId'leri string'e dönüştür
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        
        return results
    except Exception as e:
        logging.error(f"Hava kalitesi verisi alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Veri alınırken hata oluştu: {str(e)}")

@router.get("/anomalies")
async def get_anomalies(
    limit: int = Query(10, description="Listede gösterilecek anomali sayısı"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Son anomalileri görüntüle"""
    logger.info(f"Son {limit} anomali isteniyor")
    
    try:
        # Veritabanından anomalileri sorgula
        cursor = db.anomalies.find().sort("detected_at", -1).limit(limit)
        anomalies = []
        
        # ObjectId dönüşümü ile anomalileri listele
        async for doc in cursor:
            # ObjectId'leri string'e dönüştür
            doc["_id"] = str(doc["_id"])
            anomalies.append(doc)
            
        logger.info(f"{len(anomalies)} anomali bulundu ve döndürüldü")
        return anomalies
    except Exception as e:
        logger.error(f"Anomalileri alırken hata: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Anomaliler alınırken bir hata oluştu: {str(e)}"
        )

@router.get("/pollution-density")
async def get_pollution_density(
    parameter: str = Query(..., description="Yoğunluğu görüntülenecek kirlilik parametresi"),
    start_time: Optional[datetime] = Query(None, description="Başlangıç zamanı"),
    end_time: Optional[datetime] = Query(None, description="Bitiş zamanı")
):
    """
    Coğrafi bölgeye göre kirlilik yoğunluğunu getirir.
    """
    try:
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
        logging.info(f"Kirlilik yoğunluğu verisi sorgulanıyor: parametre={parameter}")
        results = await db.aggregate_pollution_data(pipeline)
        return results
    except Exception as e:
        logging.error(f"Kirlilik yoğunluğu verisi alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Veri alınırken hata oluştu: {str(e)}") 