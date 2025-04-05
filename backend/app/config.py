import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Settings:
    def __init__(self):
        # API yapılandırması
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        # MongoDB bağlantı bilgileri
        self.MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/air_quality_db")
        self.MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "air_quality_db")

        # RabbitMQ bağlantı bilgileri
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
        self.RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
        self.RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
        self.RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
        
        # WHO standartlarına göre hava kirliliği eşik değerleri (μg/m³)
        self.THRESHOLD_PM25 = float(os.getenv("THRESHOLD_PM25", "25"))  # PM2.5 24-saatlik ortalama
        self.THRESHOLD_PM10 = float(os.getenv("THRESHOLD_PM10", "50"))  # PM10 24-saatlik ortalama
        self.THRESHOLD_NO2 = float(os.getenv("THRESHOLD_NO2", "200"))   # NO2 1-saatlik ortalama
        self.THRESHOLD_SO2 = float(os.getenv("THRESHOLD_SO2", "500"))   # SO2 10-dakikalık ortalama
        self.THRESHOLD_O3 = float(os.getenv("THRESHOLD_O3", "100"))     # O3 8-saatlik ortalama

    @property
    def RABBITMQ_URL(self) -> str:
        """RabbitMQ bağlantı URL'ini oluşturur."""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"

# Settings nesnesi oluştur
settings = Settings() 