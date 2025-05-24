#!/usr/bin/env python
import json
import os
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# MongoDB bağlantı bilgileri - Docker Compose ile çalıştırıldığında
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://admin:password@mongodb:27017/air_quality_db?authSource=admin")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "air_quality_db")

# Şehir verileri - gerçek konumlar
CITIES = [
    {"name": "İstanbul", "location": {"type": "Point", "coordinates": [41.0082, 28.9784]}},
    {"name": "Ankara", "location": {"type": "Point", "coordinates": [39.9334, 32.8597]}},
    {"name": "Niğde", "location": {"type": "Point", "coordinates": [37.9667, 34.6792]}},
    {"name": "Yalova", "location": {"type": "Point", "coordinates": [40.6500, 29.2667]}},
    {"name": "Kütahya", "location": {"type": "Point", "coordinates": [39.4200, 29.9833]}},
    {"name": "Erzurum", "location": {"type": "Point", "coordinates": [39.9054, 41.2658]}},
    {"name": "Rize", "location": {"type": "Point", "coordinates": [41.0201, 40.5234]}},
    {"name": "Mardin", "location": {"type": "Point", "coordinates": [37.3212, 40.7245]}},
    {"name": "Kocaeli", "location": {"type": "Point", "coordinates": [40.7667, 29.9167]}}
]

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

def generate_air_quality_status(pm25):
    """PM2.5 değerine göre hava kalitesi durumunu belirler."""
    if pm25 <= 15:
        return "good"
    elif pm25 <= 50:
        return "moderate"
    elif pm25 <= 100:
        return "unhealthy"
    elif pm25 <= 150:
        return "very-unhealthy"
    else:
        return "hazardous"

def generate_random_air_quality_data(city):
    """Gerçekçi rastgele hava kalitesi verileri oluşturur."""
    # Şehirlere göre farklı hava kalitesi eğilimleri
    city_profiles = {
        "İstanbul": {"pm25_range": (30, 45), "pm10_range": (45, 65)},
        "Ankara": {"pm25_range": (10, 20), "pm10_range": (20, 35)},
        "Niğde": {"pm25_range": (20, 25), "pm10_range": (30, 40)},
        "Yalova": {"pm25_range": (15, 22), "pm10_range": (25, 35)},
        "Kütahya": {"pm25_range": (40, 50), "pm10_range": (65, 80)},
        "Erzurum": {"pm25_range": (75, 95), "pm10_range": (110, 130)},
        "Rize": {"pm25_range": (20, 30), "pm10_range": (35, 45)},
        "Mardin": {"pm25_range": (110, 130), "pm10_range": (150, 170)},
        "Kocaeli": {"pm25_range": (85, 105), "pm10_range": (130, 150)}
    }
    
    profile = city_profiles.get(city["name"], {"pm25_range": (10, 50), "pm10_range": (20, 80)})
    
    # Temel kirlilik değerleri
    pm25 = random.uniform(*profile["pm25_range"])
    pm10 = random.uniform(*profile["pm10_range"])
    no2 = random.uniform(10, 50)
    so2 = random.uniform(2, 25)
    o3 = random.uniform(25, 90)
    
    # Hava kalitesi durumunu belirle
    status = generate_air_quality_status(pm25)
    
    # Veri oluştur
    return {
        "location": city["location"],
        "pm25": round(pm25, 1),
        "pm10": round(pm10, 1),
        "no2": round(no2, 1),
        "so2": round(so2, 1),
        "o3": round(o3, 1),
        "status": status,
        "city": city["name"],
        "timestamp": datetime.now()
    }

def generate_anomaly_data(city, pm25_value):
    """Anomali verisi oluşturur."""
    anomaly_types = ["threshold_exceeded", "sudden_increase", "who_limit_exceeded"]
    anomaly_type = random.choice(anomaly_types)
    
    anomaly_data = {
        "location": city["location"],
        "parameter": "pm25",
        "value": pm25_value,
        "type": anomaly_type,
        "detected_at": datetime.now(),
        "city": city["name"]
    }
    
    if anomaly_type == "threshold_exceeded":
        anomaly_data["threshold"] = 50
    elif anomaly_type == "sudden_increase":
        anomaly_data["previous_value"] = pm25_value / 2
    elif anomaly_type == "who_limit_exceeded":
        anomaly_data["threshold"] = 15  # WHO PM2.5 limiti
    
    return anomaly_data

def add_data_to_mongodb():
    """Verileri MongoDB'ye ekler."""
    db = connect_to_mongodb()
    
    # Koleksiyonları temizle (isteğe bağlı)
    clear_collections = input("Koleksiyonları temizlemek istiyor musunuz? (e/h): ").lower() == 'e'
    if clear_collections:
        db.air_quality_data.delete_many({})
        db.anomalies.delete_many({})
        logger.info("Koleksiyonlar temizlendi.")
    
    # Her şehir için veri oluştur ve ekle
    air_quality_data = []
    anomaly_data = []
    
    # Geçmiş veri oluşturma
    for city in CITIES:
        # Son 24 saat için veri oluştur (1 saat aralıklarla)
        for hour in range(24, 0, -1):
            time_point = datetime.now() - timedelta(hours=hour)
            aq_data = generate_random_air_quality_data(city)
            aq_data["timestamp"] = time_point
            air_quality_data.append(aq_data)
    
    # Son veri için
    for city in CITIES:
        # Güncel veri
        aq_data = generate_random_air_quality_data(city)
        air_quality_data.append(aq_data)
        
        # Eğer PM2.5 değeri yüksekse anomali oluştur
        if aq_data["pm25"] > 50 or (city["name"] in ["Mardin", "Erzurum", "Kocaeli"]):
            anomaly_data.append(generate_anomaly_data(city, aq_data["pm25"]))
    
    # Verileri MongoDB'ye ekle
    if air_quality_data:
        db.air_quality_data.insert_many(air_quality_data)
        logger.info(f"{len(air_quality_data)} hava kalitesi verisi eklendi.")
    
    if anomaly_data:
        db.anomalies.insert_many(anomaly_data)
        logger.info(f"{len(anomaly_data)} anomali verisi eklendi.")
    
    return len(air_quality_data), len(anomaly_data)

if __name__ == "__main__":
    print("Gerçek Şehir Verileri Ekleme Aracı")
    print("----------------------------------")
    
    try:
        num_aq_data, num_anomaly_data = add_data_to_mongodb()
        print(f"\nToplam {num_aq_data} hava kalitesi verisi ve {num_anomaly_data} anomali verisi eklendi.")
        print("\nVerileri görüntülemek için test_mongodb_direct.py scriptini çalıştırın:")
        print("python scripts/test_mongodb_direct.py")
    except Exception as e:
        logger.error(f"Veri ekleme sırasında hata oluştu: {e}")
        sys.exit(1) 