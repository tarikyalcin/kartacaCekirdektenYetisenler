import asyncio
import json
import logging
from datetime import datetime
import aio_pika
from aio_pika import connect_robust, ExchangeType, Message

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RabbitMQ bağlantı bilgileri - Docker Compose'dan alındı
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5673
RABBITMQ_USER = "admin"
RABBITMQ_PASS = "password"
RABBITMQ_VHOST = "/"

class RabbitMQ:
    """
    Test için basitleştirilmiş RabbitMQ sınıfı
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queues = {}
    
    async def connect(self):
        """
        RabbitMQ'ya bağlanır, bağlantıyı ve kanalı oluşturur
        """
        try:
            # Bağlantı URL'si oluştur
            connection_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
            
            # Bağlantı kur
            self.connection = await connect_robust(connection_url)
            
            # Kanal oluştur
            self.channel = await self.connection.channel()
            
            # Exchange oluştur (topic tipinde)
            self.exchange = await self.channel.declare_exchange(
                "air_quality_exchange", ExchangeType.TOPIC, durable=True
            )
            
            logger.info(f"RabbitMQ bağlantısı kuruldu: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            
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
        
        # Anomali bildirimleri kuyruğu
        anomaly_queue = await self.channel.declare_queue(
            "anomaly_notifications", durable=True
        )
        await anomaly_queue.bind(self.exchange, "anomaly.#")
        self.queues["anomaly_notifications"] = anomaly_queue
        logger.info("RabbitMQ anomaly_notifications kuyruğu oluşturuldu")
    
    async def get_message(self, queue_name):
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
            # no_wait=True parametresi, mesaj yoksa beklemeden None döndürür
            message = await self.queues[queue_name].get(fail=False)
            
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
    
    async def close(self):
        """RabbitMQ bağlantısını kapatır"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None
            self.queues = {}
            logger.info("RabbitMQ bağlantısı kapatıldı")

# RabbitMQ'dan gelen anomali bildirimlerini dinlemek için test fonksiyonu
async def listen_for_anomalies(rabbitmq):
    """
    RabbitMQ'dan anomali bildirimlerini dinler ve konsola yazdırır
    """
    logger.info("Anomali dinleme görevi başladı")
    
    try:
        while True:
            try:
                # Anomali kuyruğundan mesaj al
                message = await rabbitmq.get_message("anomaly_notifications")
                if message:
                    logger.info(f"Yeni anomali mesajı alındı: {json.dumps(message, indent=2)}")
                    
                    # Gerçek WebSocket kodunda bu noktada mesaj WebSocket üzerinden gönderilir
                    # await manager.broadcast({"type": "new_anomaly", "data": message}, "anomalies")
            except Exception as e:
                logger.error(f"Anomali mesajı alınırken hata: {str(e)}")
            
            # Kısa bir süre bekle
            await asyncio.sleep(0.5)
            
    except asyncio.CancelledError:
        logger.info("Anomali dinleme görevi sonlandırıldı")
    except Exception as e:
        logger.error(f"Anomali dinleme sırasında hata: {str(e)}")

async def main():
    # RabbitMQ bağlantısı kur
    rabbitmq = RabbitMQ()
    await rabbitmq.connect()
    await rabbitmq.setup_queues()
    
    try:
        # Dinleme görevini başlat
        listener_task = asyncio.create_task(listen_for_anomalies(rabbitmq))
        
        # Kullanıcı girdisini bekle
        print("\nAnomaliler dinleniyor. Çıkmak için Enter tuşuna basın...")
        
        # Asenkron olarak kullanıcı girdisi al
        await asyncio.to_thread(input)
        
        # Dinleme görevini iptal et
        listener_task.cancel()
        await asyncio.gather(listener_task, return_exceptions=True)
        
    finally:
        # RabbitMQ bağlantısını kapat
        await rabbitmq.close()

if __name__ == "__main__":
    asyncio.run(main()) 