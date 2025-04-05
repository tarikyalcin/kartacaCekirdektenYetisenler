import aio_pika
import json
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from app.config import settings
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

# Tarih/zaman ve ObjectId nesneleri için özel JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    """
    datetime ve ObjectId nesnelerini uygun formatlara dönüştüren özel JSON encoder
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class RabbitMQ:
    """
    RabbitMQ bağlantısı, kanal ve exchange yönetimi için sınıf
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.max_retries = 5
        self.retry_delay = 5  # saniye
    
    async def connect(self):
        """
        RabbitMQ'ya bağlanır, bağlantıyı ve kanalı oluşturur
        """
        rabbitmq_url = settings.RABBITMQ_URL
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"RabbitMQ bağlantısı kuruluyor: {rabbitmq_url}")
                self.connection = await aio_pika.connect_robust(rabbitmq_url)
                self.channel = await self.connection.channel()
                self.exchange = await self.channel.declare_exchange(
                    "air_quality_exchange", 
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                logger.info("RabbitMQ bağlantısı başarıyla kuruldu")
                return
            except Exception as e:
                logger.warning(f"RabbitMQ bağlantısı kurulamadı, {self.retry_delay} saniye sonra yeniden deneniyor. Deneme: {attempt+1}/{self.max_retries}. Hata: {str(e)}")
                if attempt == self.max_retries - 1:
                    # Son denemede de başarısız olursa hata fırlat
                    logger.error(f"RabbitMQ bağlantısı {self.max_retries} denemeden sonra başarısız oldu: {str(e)}")
                    raise
                await asyncio.sleep(self.retry_delay)
    
    async def setup_queues(self):
        """
        Gerekli kuyrukları ve binding'leri oluşturur
        """
        if not self.channel:
            raise ValueError("Önce RabbitMQ'ya bağlanmalısınız")
        
        try:
            # Ham veri kuyruğu
            raw_queue = await self.channel.declare_queue("raw_data", durable=True)
            await raw_queue.bind(self.exchange, "data.raw")
            
            # İşlenmiş veri kuyruğu
            processed_queue = await self.channel.declare_queue("processed_data", durable=True)
            await processed_queue.bind(self.exchange, "data.processed")
            
            # Anomali bildirimi kuyruğu
            notification_queue = await self.channel.declare_queue("anomaly_notifications", durable=True)
            await notification_queue.bind(self.exchange, "notification.anomaly")
            
            logger.info("RabbitMQ kuyrukları başarıyla oluşturuldu")
        except Exception as e:
            logger.error(f"RabbitMQ kuyrukları oluşturulurken hata: {str(e)}")
            raise
    
    async def publish(self, routing_key: str, message: Dict[str, Any]):
        """
        Belirtilen routing key ile bir mesaj yayınlar
        
        Args:
            routing_key (str): Mesajın yönlendirileceği routing key
            message (Dict[str, Any]): Yayınlanacak mesaj içeriği
        """
        if not self.exchange:
            raise ValueError("Önce RabbitMQ'ya bağlanmalısınız")
        
        try:
            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message, cls=CustomJSONEncoder).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=routing_key
            )
        except Exception as e:
            logger.error(f"Mesaj yayınlanırken hata: {str(e)}")
            raise
    
    async def consume(self, queue_name: str, callback):
        """
        Belirtilen kuyruktan mesaj tüketir
        
        Args:
            queue_name (str): Tüketilecek kuyruğun adı
            callback (Callable): Mesaj alındığında çağrılacak fonksiyon
        """
        if not self.channel:
            raise ValueError("Önce RabbitMQ'ya bağlanmalısınız")
        
        try:
            queue = await self.channel.get_queue(queue_name)
            await queue.consume(callback)
            logger.info(f"'{queue_name}' kuyruğundan tüketim başlatıldı")
        except Exception as e:
            logger.error(f"Mesaj tüketimi başlatılırken hata: {str(e)}")
            raise
    
    async def close(self):
        """
        RabbitMQ bağlantısını kapatır
        """
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None
            logger.info("RabbitMQ bağlantısı kapatıldı")

# Singleton instance
rabbitmq = RabbitMQ() 