import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.services.database import db
from app.services.rabbitmq import rabbitmq, CustomJSONEncoder
from app.services.anomaly_detection import anomaly_detector
from app.models.air_quality import AirQualityData, AirQualityAnomaly

logger = logging.getLogger(__name__)

class Worker:
    """
    Backend işleri yürüten worker servisi.
    Mesaj kuyruğundan verileri alır, işler ve veritabanına kaydeder.
    """
    
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """
        Worker servisini başlatır.
        """
        if self.running:
            logger.warning("Worker servisi zaten çalışıyor")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Worker servisi başlatıldı")
    
    async def stop(self):
        """
        Worker servisini durdurur.
        """
        if not self.running:
            logger.warning("Worker servisi zaten durdurulmuş")
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        logger.info("Worker servisi durduruldu")
    
    async def _run(self):
        """
        Worker'ın ana döngüsü.
        """
        logger.info("Worker döngüsü başladı")
        
        # Mesaj işleme callback fonksiyonu
        async def process_message(message):
            async with message.process():
                await self._process_data(json.loads(message.body))
        
        # RabbitMQ tüketici başlat
        await rabbitmq.consume("raw_data", process_message)
        
        # Servis durdurulana kadar bekle
        while self.running:
            await asyncio.sleep(1)
    
    async def _process_data(self, data: Dict[str, Any]):
        """
        Ham veriyi işler, anomali kontrolü yapar ve veritabanına kaydeder.
        
        Args:
            data (Dict[str, Any]): İşlenecek ham veri
        """
        try:
            # Veriyi modele dönüştür
            air_quality_data = AirQualityData(**data)
            
            # Veriyi veritabanına kaydet
            mongo_doc = air_quality_data.to_mongo_document()
            await db.insert_air_quality_data(mongo_doc)
            
            # Anomali kontrolü yap
            threshold_anomalies = await anomaly_detector.check_threshold_anomaly(air_quality_data)
            historical_anomalies = await anomaly_detector.check_historical_anomaly(air_quality_data)
            
            # Tüm anomalileri birleştir
            all_anomalies = []
            if threshold_anomalies:
                all_anomalies.extend(threshold_anomalies)
            if historical_anomalies:
                all_anomalies.extend(historical_anomalies)
            
            # Anomalileri veritabanına kaydet ve bildirim yap
            if all_anomalies:
                for anomaly in all_anomalies:
                    # Anomaliyi veritabanına kaydet
                    anomaly_doc = anomaly.to_mongo_document()
                    await db.insert_anomaly(anomaly_doc)
                    
                    # Anomali bildirimi gönder
                    await self._send_anomaly_notification(anomaly)
            
            # İşlenmiş veriyi diğer servislere ilet
            await self._send_processed_data(air_quality_data, all_anomalies)
            
            logger.info(
                f"Veri işlendi: {air_quality_data.latitude}, {air_quality_data.longitude}, "
                f"anomali sayısı: {len(all_anomalies) if all_anomalies else 0}"
            )
            
        except Exception as e:
            logger.error(f"Veri işlenirken hata: {str(e)}")
    
    async def _send_anomaly_notification(self, anomaly: AirQualityAnomaly):
        """
        Anomali bildirimi gönderir.
        
        Args:
            anomaly (AirQualityAnomaly): Anomali verisi
        """
        try:
            # Anomali verisini bildirim formatına dönüştür
            notification = {
                "type": "anomaly",
                "data": anomaly.to_mongo_document(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Routing key oluştur (anomalinin tipine göre)
            parameter = anomaly.parameter
            severity = anomaly.severity
            routing_key = f"anomaly.{parameter}.{severity}"
            
            # RabbitMQ'ya bildirim gönder
            await rabbitmq.publish(routing_key, notification)
            
            logger.info(
                f"Anomali bildirimi gönderildi: {parameter}, "
                f"değer: {anomaly.actual_value}, şiddet: {severity}"
            )
            
        except Exception as e:
            logger.error(f"Anomali bildirimi gönderilirken hata: {str(e)}")
    
    async def _send_processed_data(self, data: AirQualityData, anomalies: Optional[List[AirQualityAnomaly]] = None):
        """
        İşlenmiş veriyi 'processed_data' kuyruğuna gönderir.
        
        Args:
            data (AirQualityData): İşlenmiş veri
            anomalies (Optional[List[AirQualityAnomaly]]): Tespit edilen anomaliler
        """
        try:
            # İşlenmiş veri mesajını oluştur
            processed_data = {
                "type": "processed_data",
                "data": data.to_mongo_document(),
                "has_anomalies": bool(anomalies),
                "anomaly_count": len(anomalies) if anomalies else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Veri analizlerini ekle (isteğe bağlı)
            analysis = await anomaly_detector.analyze_and_predict(data)
            if analysis:
                processed_data["analysis"] = analysis
            
            # RabbitMQ'ya işlenmiş veriyi gönder
            await rabbitmq.publish("data.processed", processed_data)
            
            logger.debug(
                f"İşlenmiş veri gönderildi: {data.latitude}, {data.longitude}"
            )
            
        except Exception as e:
            logger.error(f"İşlenmiş veri gönderilirken hata: {str(e)}")

# Singleton instance
worker = Worker() 