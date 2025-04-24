import aio_pika
import json
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from app.config import settings
from datetime import datetime
from bson import ObjectId
from aio_pika import connect_robust, Message, ExchangeType

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
        self.queues = {}
        self.max_retries = 5
        self.retry_delay = 5  # saniye
    
    async def connect(self):
        """
        RabbitMQ'ya bağlanır, bağlantıyı ve kanalı oluşturur
        """
        try:
            # Bağlantı URL'si oluştur
            connection_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}"
            
            # Bağlantı kur
            self.connection = await connect_robust(connection_url)
            
            # Kanal oluştur
            self.channel = await self.connection.channel()
            
            # Exchange oluştur (topic tipinde)
            self.exchange = await self.channel.declare_exchange(
                "air_quality_exchange", ExchangeType.TOPIC, durable=True
            )
            
            logger.info(f"RabbitMQ bağlantısı kuruldu: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
            
        except Exception as e:
            logger.error(f"RabbitMQ bağlantısı kurulamadı: {str(e)}")
            self.connection = None
            self.channel = None
            self.exchange = None
            raise
    
    async def setup_queues(self):
        """
        Gerekli kuyrukları ve binding'leri oluşturur
        """
        if not self.channel or not self.exchange:
            raise Exception("RabbitMQ bağlantısı kurulmadan kuyruklar oluşturulamaz")
        
        # Ham veri kuyruğu
        raw_data_queue = await self.channel.declare_queue(
            "raw_data", durable=True
        )
        await raw_data_queue.bind(self.exchange, "data.raw")
        self.queues["raw_data"] = raw_data_queue
        logger.info("RabbitMQ raw_data kuyruğu oluşturuldu")
        
        # İşlenmiş veri kuyruğu
        processed_data_queue = await self.channel.declare_queue(
            "processed_data", durable=True
        )
        await processed_data_queue.bind(self.exchange, "data.processed")
        self.queues["processed_data"] = processed_data_queue
        logger.info("RabbitMQ processed_data kuyruğu oluşturuldu")
        
        # Anomali bildirimleri kuyruğu
        anomaly_queue = await self.channel.declare_queue(
            "anomaly_notifications", durable=True
        )
        await anomaly_queue.bind(self.exchange, "anomaly.#")
        self.queues["anomaly_notifications"] = anomaly_queue
        logger.info("RabbitMQ anomaly_notifications kuyruğu oluşturuldu")
    
    async def publish(self, routing_key: str, data: Dict[str, Any]):
        """
        Exchange'e mesaj yayınlar.
        
        Args:
            routing_key (str): Yönlendirme anahtarı
            data (Dict[str, Any]): Yayınlanacak veri
        """
        if not self.exchange:
            raise Exception("RabbitMQ bağlantısı kurulmadan mesaj yayınlanamaz")
        
        # Veriyi JSON formatına dönüştür
        message_body = json.dumps(data, cls=CustomJSONEncoder).encode()
        
        # Mesaj oluştur
        message = Message(
            message_body,
            content_type="application/json",
            timestamp=datetime.utcnow().timestamp(),
            headers={"source": "api"}
        )
        
        # Mesajı yayınla
        await self.exchange.publish(message, routing_key=routing_key)
        logger.debug(f"Mesaj yayınlandı: {routing_key}")
    
    async def get_message(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Belirtilen kuyruktan bir mesaj alır.
        
        Args:
            queue_name (str): Mesajın alınacağı kuyruk adı
            
        Returns:
            Optional[Dict[str, Any]]: Alınan mesaj, kuyruk boşsa None
        """
        if not self.channel or queue_name not in self.queues:
            raise Exception(f"RabbitMQ {queue_name} kuyruğu bulunamadı")
        
        # Kuyruktan mesaj al
        try:
            message = await self.queues[queue_name].get()
            
            if message:
                try:
                    # Mesajı işaretleme (acknowledgment)
                    await message.ack()
                    
                    # Mesaj içeriğini JSON olarak çözümle
                    message_body = message.body.decode()
                    data = json.loads(message_body)
                    return data
                except Exception as e:
                    logger.error(f"Mesaj işlenirken hata: {str(e)}")
                    await message.nack(requeue=True)  # Hata durumunda mesajı kuyruğa geri koy
        except Exception as e:
            logger.error(f"Mesaj alınırken hata: {str(e)}")
            
        return None
    
    async def consume(self, queue_name: str, callback):
        """
        Belirtilen kuyruktan mesajları tüketmek için bir tüketici başlatır.
        
        Args:
            queue_name (str): Mesajların tüketileceği kuyruk adı
            callback: Mesaj alındığında çağrılacak fonksiyon
        """
        if not self.channel or queue_name not in self.queues:
            raise Exception(f"RabbitMQ {queue_name} kuyruğu bulunamadı")
        
        # Tüketme işlemi başlat
        await self.queues[queue_name].consume(callback)
        logger.info(f"RabbitMQ {queue_name} kuyruğundan tüketim başladı")
    
    async def close(self):
        """
        RabbitMQ bağlantısını kapatır
        """
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None
            self.queues = {}
            logger.info("RabbitMQ bağlantısı kapatıldı")

# Singleton instance
rabbitmq = RabbitMQ() 