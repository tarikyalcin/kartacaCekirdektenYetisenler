import json
import logging
import asyncio
from typing import Dict, Any, Callable, List
from app.models.air_quality import AirQualityData
from app.services.database import db
from app.services.rabbitmq import rabbitmq
from app.services.anomaly_detection import anomaly_detector

logger = logging.getLogger(__name__)

class Worker:
    """
    RabbitMQ'dan gelen mesajları işleyen ve anomali tespiti yapan worker servisi.
    """
    
    def __init__(self):
        self.running = False
        self.tasks = []
        self.max_retries = 3
        self.retry_delay = 10  # saniye
    
    async def start(self):
        """
        Worker servisini başlatır.
        """
        if self.running:
            logger.warning("Worker zaten çalışıyor.")
            return
        
        self.running = True
        logger.info("Worker başlatılıyor...")
        
        # RabbitMQ'dan ham veri mesajlarını işlemek için callback fonksiyonu
        async def process_raw_data(message):
            async with message.process():
                # Mesaj içeriğini JSON'dan Python nesnesine dönüştür
                try:
                    body = message.body.decode()
                    data_dict = json.loads(body)
                    logger.info(f"Ham veri alındı: {data_dict}")
                    
                    # AirQualityData nesnesine dönüştür
                    data = AirQualityData(**data_dict)
                    
                    # Veriyi MongoDB'ye kaydet
                    mongo_doc = data.to_mongo_document()
                    result_id = await db.insert_air_quality_data(mongo_doc)
                    logger.info(f"Veri MongoDB'ye kaydedildi. ID: {result_id}")
                    
                    # Anomali tespiti yap (eşik değerlerine göre)
                    threshold_anomalies = await anomaly_detector.check_threshold_anomaly(data)
                    
                    # Anomali varsa işle
                    if threshold_anomalies:
                        for anomaly in threshold_anomalies:
                            # Anomaliyi MongoDB'ye kaydet
                            anomaly_doc = anomaly.to_mongo_document()
                            anomaly_id = await db.insert_anomaly(anomaly_doc)
                            logger.info(f"Eşik anomalisi kaydedildi. ID: {anomaly_id}")
                            
                            # Anomali bildirimini RabbitMQ'ya gönder
                            await rabbitmq.publish(
                                "notification.anomaly", 
                                {
                                    "type": "threshold",
                                    "anomaly_id": anomaly_id,
                                    "parameter": anomaly.parameter,
                                    "severity": anomaly.severity,
                                    "location": {
                                        "latitude": anomaly.data.latitude,
                                        "longitude": anomaly.data.longitude,
                                        "city": anomaly.data.city,
                                        "country": anomaly.data.country
                                    }
                                }
                            )
                    
                    # Tarihsel verilere göre anomali tespiti yap (Z-score)
                    historical_anomalies = await anomaly_detector.check_historical_anomaly(data)
                    
                    # Anomali varsa işle
                    if historical_anomalies:
                        for anomaly in historical_anomalies:
                            # Anomaliyi MongoDB'ye kaydet
                            anomaly_doc = anomaly.to_mongo_document()
                            anomaly_id = await db.insert_anomaly(anomaly_doc)
                            logger.info(f"Z-score anomalisi kaydedildi. ID: {anomaly_id}")
                            
                            # Anomali bildirimini RabbitMQ'ya gönder
                            await rabbitmq.publish(
                                "notification.anomaly", 
                                {
                                    "type": "z-score",
                                    "anomaly_id": anomaly_id,
                                    "parameter": anomaly.parameter,
                                    "severity": anomaly.severity,
                                    "location": {
                                        "latitude": anomaly.data.latitude,
                                        "longitude": anomaly.data.longitude,
                                        "city": anomaly.data.city,
                                        "country": anomaly.data.country
                                    }
                                }
                            )
                    
                    # İşlenmiş veriyi "data.processed" routing key'i ile RabbitMQ'ya gönder
                    await rabbitmq.publish("data.processed", mongo_doc)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON çözümleme hatası: {str(e)}")
                except Exception as e:
                    logger.error(f"Veri işleme hatası: {str(e)}")
        
        # Ham veri kuyruğunu tüket - birkaç kez yeniden deneme yapabilir
        for attempt in range(self.max_retries):
            try:
                # RabbitMQ servisinin başlamış olduğundan emin olmak için bekleme
                if attempt > 0:
                    logger.info(f"Worker RabbitMQ bağlantısı için {self.retry_delay} saniye bekleniyor (deneme {attempt+1}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                
                # RabbitMQ tüketici başlat
                await rabbitmq.consume("raw_data", process_raw_data)
                logger.info("RabbitMQ raw_data kuyruğu tüketiliyor")
                break  # Başarılıysa döngüden çık
            except Exception as e:
                logger.error(f"RabbitMQ tüketici başlatma hatası (deneme {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Maksimum deneme sayısına ulaşıldı. Worker başlatılamadı.")
                    self.running = False
                    # Hatayı yükseltmeyelim, sadece worker'ı durduralım
        
        # Worker başlatıldı ve RabbitMQ consumer aktif
        if self.running:
            logger.info("Worker servisi başarıyla başlatıldı")
    
    async def stop(self):
        """
        Worker servisini durdurur.
        """
        if not self.running:
            logger.warning("Worker zaten durdurulmuş.")
            return
        
        self.running = False
        logger.info("Worker durduruluyor...")
        
        # Tüm görevleri iptal et
        for task in self.tasks:
            task.cancel()
        
        logger.info("Worker durduruldu.")

# Singleton instance
worker = Worker() 