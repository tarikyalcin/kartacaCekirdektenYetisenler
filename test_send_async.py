import asyncio
import json
from datetime import datetime
import aio_pika
from aio_pika import ExchangeType, Message, connect_robust

# RabbitMQ bağlantı bilgileri - Docker Compose'dan alındı
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5673
RABBITMQ_USER = "admin"
RABBITMQ_PASS = "password"
RABBITMQ_VHOST = "/"

async def send_test_message():
    # Bağlantı URL'si
    connection_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    
    # RabbitMQ'ya bağlan
    connection = await connect_robust(connection_url)
    
    try:
        # Kanal oluştur
        channel = await connection.channel()
        
        # Exchange oluştur (topic tipinde)
        exchange = await channel.declare_exchange(
            "air_quality_exchange", ExchangeType.TOPIC, durable=True
        )
        
        # Anomali mesajı oluştur
        anomaly_data = {
            "id": "test_anomaly_id",
            "device_id": "test_device_001",
            "timestamp": datetime.now().isoformat(),
            "anomaly_type": "high_pollution",
            "location": {
                "latitude": 41.0082,
                "longitude": 28.9784
            },
            "values": {
                "pm25": 120.5,
                "pm10": 180.2,
                "co2": 2800,
                "tvoc": 980
            },
            "description": "Yüksek partikül madde seviyeleri tespit edildi",
            "severity": "high",
            "status": "active"
        }
        
        # JSON formatına dönüştür
        message_body = json.dumps(anomaly_data).encode()
        
        # Mesajı gönder
        await exchange.publish(
            Message(
                body=message_body,
                content_type="application/json",
                delivery_mode=2  # Persistent mesaj
            ),
            routing_key="anomaly.high_pollution"
        )
        
        print(f"Test anomali mesajı gönderildi: {json.dumps(anomaly_data, indent=2)}")
        
    finally:
        # Bağlantıyı kapat
        await connection.close()

if __name__ == "__main__":
    asyncio.run(send_test_message()) 