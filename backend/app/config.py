import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API yapılandırması
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# MongoDB bağlantı bilgileri
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "air_quality_db")
MONGO_COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA", "air_quality_data")
MONGO_COLLECTION_ANOMALIES = os.getenv("MONGO_COLLECTION_ANOMALIES", "air_quality_anomalies")

# RabbitMQ bağlantı bilgileri
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# RabbitMQ kuyruk isimleri
QUEUE_RAW_DATA = "air_quality_raw_data"
QUEUE_PROCESSED_DATA = "air_quality_processed_data"
QUEUE_ANOMALIES = "air_quality_anomalies"

# WHO standartlarına göre hava kirliliği eşik değerleri (μg/m³)
THRESHOLD_PM25 = float(os.getenv("THRESHOLD_PM25", "25"))  # PM2.5 24-saatlik ortalama
THRESHOLD_PM10 = float(os.getenv("THRESHOLD_PM10", "50"))  # PM10 24-saatlik ortalama
THRESHOLD_NO2 = float(os.getenv("THRESHOLD_NO2", "200"))   # NO2 1-saatlik ortalama
THRESHOLD_SO2 = float(os.getenv("THRESHOLD_SO2", "500"))   # SO2 10-dakikalık ortalama
THRESHOLD_O3 = float(os.getenv("THRESHOLD_O3", "100"))     # O3 8-saatlik ortalama 