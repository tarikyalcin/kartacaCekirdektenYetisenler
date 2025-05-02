#!/usr/bin/env python
import json
import os
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# MongoDB bağlantı bilgileri
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://admin:password@localhost:27017/air_quality_db?authSource=admin")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "air_quality_db")

# Datetime nesnelerini JSON'a dönüştürmek için özel encoder
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def connect_to_mongodb():
    """MongoDB'ye bağlanır ve veritabanı nesnesini döndürür."""
    try:
        client = MongoClient(MONGODB_URL)
        db = client[MONGODB_DB_NAME]
        logger.info(f"MongoDB bağlantısı başarılı: {MONGODB_DB_NAME}")
        return db
    except Exception as e:
        logger.error(f"MongoDB bağlantı hatası: {e}")
        sys.exit(1)

def get_air_quality_data(db, limit=100):
    """Son 100 hava kalitesi verisini getirir."""
    try:
        collection = db.air_quality_data
        # Son eklenen verileri al
        cursor = collection.find().sort([("timestamp", -1)]).limit(limit)
        
        data = []
        for doc in cursor:
            # ObjectId JSON serileştirilemez, bu yüzden string'e çeviriyoruz
            doc["_id"] = str(doc["_id"])
            
            # Timestamp'i ISO formatına çeviriyoruz (eğer datetime nesnesi ise)
            if isinstance(doc.get("timestamp"), datetime):
                doc["timestamp"] = doc["timestamp"].isoformat()
                
            data.append(doc)
            
        logger.info(f"{len(data)} hava kalitesi verisi alındı")
        return data
    except Exception as e:
        logger.error(f"Veri alınırken hata oluştu: {e}")
        return []

def get_anomaly_data(db, limit=20):
    """Son 20 anomali verisini getirir."""
    try:
        collection = db.anomalies
        # Son anomalileri al
        cursor = collection.find().sort([("detected_at", -1)]).limit(limit)
        
        data = []
        for doc in cursor:
            # ObjectId JSON serileştirilemez, bu yüzden string'e çeviriyoruz
            doc["_id"] = str(doc["_id"])
            
            # Timestamp'i ISO formatına çeviriyoruz (eğer datetime nesnesi ise)
            if isinstance(doc.get("detected_at"), datetime):
                doc["detected_at"] = doc["detected_at"].isoformat()
                
            data.append(doc)
            
        logger.info(f"{len(data)} anomali verisi alındı")
        return data
    except Exception as e:
        logger.error(f"Anomali verileri alınırken hata oluştu: {e}")
        return []

def get_stats_data(db):
    """İstatistik verilerini hesaplar."""
    try:
        air_quality_collection = db.air_quality_data
        anomaly_collection = db.anomalies
        
        # Son 24 saat içindeki verileri filtrele
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        # Anomali sayısı
        total_alerts = anomaly_collection.count_documents({
            "detected_at": {"$gte": twenty_four_hours_ago}
        })
        
        # WHO limitini aşan kayıt sayısı (WHO PM2.5 limiti: 15 µg/m³)
        who_limit_exceeded = air_quality_collection.count_documents({
            "timestamp": {"$gte": twenty_four_hours_ago},
            "pm25": {"$gt": 15}  # WHO PM2.5 limit değeri
        })
        
        # Ani artış sayısı (anomalilerde type=sudden_increase olanlar)
        sudden_increases = anomaly_collection.count_documents({
            "detected_at": {"$gte": twenty_four_hours_ago},
            "type": "sudden_increase"
        })
        
        # Etkilenen benzersiz bölgeler
        pipeline = [
            {"$match": {"timestamp": {"$gte": twenty_four_hours_ago}}},
            {"$group": {"_id": {"lat": "$location.coordinates.0", "lng": "$location.coordinates.1"}}},
            {"$count": "count"}
        ]
        affected_regions_result = list(air_quality_collection.aggregate(pipeline))
        affected_regions = affected_regions_result[0]["count"] if affected_regions_result else 0
        
        # En yüksek PM2.5 değeri
        highest_value_doc = air_quality_collection.find_one(
            {"timestamp": {"$gte": twenty_four_hours_ago}},
            sort=[("pm25", -1)]
        )
        highest_value = highest_value_doc["pm25"] if highest_value_doc else 0
        
        stats = {
            "totalAlerts": total_alerts,
            "whoLimitExceeded": who_limit_exceeded,
            "suddenIncreases": sudden_increases,
            "affectedRegions": affected_regions,
            "highestValue": highest_value
        }
        
        logger.info("İstatistik verileri hesaplandı")
        return stats
    except Exception as e:
        logger.error(f"İstatistik verileri hesaplanırken hata oluştu: {e}")
        return {
            "totalAlerts": 0,
            "whoLimitExceeded": 0,
            "suddenIncreases": 0,
            "affectedRegions": 0,
            "highestValue": 0
        }

def export_data_to_json():
    """Tüm verileri JSON dosyalarına aktarır."""
    try:
        db = connect_to_mongodb()
        
        # Verileri topla
        air_quality_data = get_air_quality_data(db)
        anomaly_data = get_anomaly_data(db)
        stats_data = get_stats_data(db)
        
        # Frontend public klasörünü kontrol et (yoksa oluştur)
        frontend_public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "public", "data")
        os.makedirs(frontend_public_dir, exist_ok=True)
        
        # Dosyaları kaydet - özel encoder kullanarak
        with open(os.path.join(frontend_public_dir, "air_quality.json"), "w") as f:
            json.dump(air_quality_data, f, indent=2, cls=DateTimeEncoder)
                
        with open(os.path.join(frontend_public_dir, "anomalies.json"), "w") as f:
            json.dump(anomaly_data, f, indent=2, cls=DateTimeEncoder)
                
        with open(os.path.join(frontend_public_dir, "stats.json"), "w") as f:
            json.dump(stats_data, f, indent=2, cls=DateTimeEncoder)
                
        logger.info(f"Veriler başarıyla {frontend_public_dir} klasörüne kaydedildi")
        
        # Ek olarak test veri seti de oluştur (eğer veritabanı boşsa)
        if not air_quality_data:
            create_test_data_json(frontend_public_dir)
            
    except Exception as e:
        logger.error(f"Dosyalar kaydedilirken hata oluştu: {e}")
        # Hata durumunda test veri seti oluştur
        frontend_public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "public", "data")
        os.makedirs(frontend_public_dir, exist_ok=True)
        create_test_data_json(frontend_public_dir)

def create_test_data_json(target_dir):
    """Veritabanında veri yoksa test verisi oluşturur."""
    # Sadece seçilen şehirler için test verileri
    test_data = [
        {"location": {"type": "Point", "coordinates": [41.0082, 28.9784]}, "pm25": 35, "pm10": 55, "no2": 25, "so2": 8, "o3": 48, "status": "moderate", "city": "İstanbul"},
        {"location": {"type": "Point", "coordinates": [39.9334, 32.8597]}, "pm25": 15, "pm10": 28, "no2": 18, "so2": 5, "o3": 30, "status": "good", "city": "Ankara"},
        {"location": {"type": "Point", "coordinates": [37.9667, 34.6792]}, "pm25": 22, "pm10": 35, "no2": 14, "so2": 4, "o3": 32, "status": "moderate", "city": "Niğde"},
        {"location": {"type": "Point", "coordinates": [40.6500, 29.2667]}, "pm25": 18, "pm10": 30, "no2": 12, "so2": 3, "o3": 28, "status": "good", "city": "Yalova"},
        {"location": {"type": "Point", "coordinates": [39.4200, 29.9833]}, "pm25": 45, "pm10": 70, "no2": 30, "so2": 12, "o3": 50, "status": "moderate", "city": "Kütahya"},
        {"location": {"type": "Point", "coordinates": [39.9054, 41.2658]}, "pm25": 85, "pm10": 120, "no2": 40, "so2": 15, "o3": 65, "status": "unhealthy", "city": "Erzurum"},
        {"location": {"type": "Point", "coordinates": [41.0201, 40.5234]}, "pm25": 25, "pm10": 40, "no2": 15, "so2": 6, "o3": 35, "status": "moderate", "city": "Rize"},
        {"location": {"type": "Point", "coordinates": [37.3212, 40.7245]}, "pm25": 120, "pm10": 160, "no2": 55, "so2": 22, "o3": 78, "status": "very-unhealthy", "city": "Mardin"},
        {"location": {"type": "Point", "coordinates": [40.7667, 29.9167]}, "pm25": 95, "pm10": 140, "no2": 45, "so2": 18, "o3": 70, "status": "unhealthy", "city": "Kocaeli"}
    ]
    
    # Her kayıt için timestamp ekle
    now = datetime.now()
    for i, item in enumerate(test_data):
        item["timestamp"] = (now - timedelta(hours=i)).isoformat()
        item["_id"] = f"test_id_{i}"
    
    # Test anomalileri - sadece İstanbul ve Mardin için
    test_anomalies = [
        {"location": {"type": "Point", "coordinates": [41.0082, 28.9784]}, "parameter": "pm25", "value": 85, "threshold": 50, "type": "threshold_exceeded", "detected_at": (now - timedelta(hours=2)).isoformat(), "city": "İstanbul"},
        {"location": {"type": "Point", "coordinates": [37.3212, 40.7245]}, "parameter": "pm25", "value": 120, "threshold": 50, "type": "threshold_exceeded", "detected_at": (now - timedelta(hours=8)).isoformat(), "city": "Mardin"}
    ]
    
    # Test istatistikleri
    test_stats = {
        "totalAlerts": 2,
        "whoLimitExceeded": 4,
        "suddenIncreases": 0,
        "affectedRegions": 9,
        "highestValue": 120
    }
    
    # Dosyaları kaydet
    try:
        with open(os.path.join(target_dir, "air_quality.json"), "w") as f:
            json.dump(test_data, f, indent=2, cls=DateTimeEncoder)
            
        with open(os.path.join(target_dir, "anomalies.json"), "w") as f:
            json.dump(test_anomalies, f, indent=2, cls=DateTimeEncoder)
            
        with open(os.path.join(target_dir, "stats.json"), "w") as f:
            json.dump(test_stats, f, indent=2, cls=DateTimeEncoder)
            
        logger.info(f"Test verileri başarıyla {target_dir} klasörüne kaydedildi")
    except Exception as e:
        logger.error(f"Test verileri kaydedilirken hata oluştu: {e}")

if __name__ == "__main__":
    export_data_to_json() 