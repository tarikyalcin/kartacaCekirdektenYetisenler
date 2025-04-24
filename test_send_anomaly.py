import pika
import json
from datetime import datetime

# RabbitMQ bağlantısı
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5673,  # Docker compose'daki port yönlendirmesine göre ayarlanmıştır
        virtual_host='/',
        credentials=pika.PlainCredentials('admin', 'password')
    )
)

channel = connection.channel()

# Exchange oluştur
channel.exchange_declare(
    exchange="air_quality_exchange",
    exchange_type="topic",
    durable=True
)

# Kuyruk oluştur ve bind et
channel.queue_declare(
    queue="anomaly_notifications",
    durable=True
)

channel.queue_bind(
    queue="anomaly_notifications",
    exchange="air_quality_exchange",
    routing_key="anomaly.pm25.critical"
)

# Test mesajı oluştur
test_message = {
    "type": "anomaly",
    "data": {
        "parameter": "pm25",
        "location": "Ankara, Türkiye",
        "latitude": 39.9334,
        "longitude": 32.8597,
        "actual_value": 180.5,
        "threshold": 100.0,
        "severity": "critical",
        "detected_at": datetime.utcnow().isoformat()
    },
    "timestamp": datetime.utcnow().isoformat()
}

# Mesajı JSON formatına dönüştür
message_body = json.dumps(test_message).encode()

# Mesajı yayınla
channel.basic_publish(
    exchange="air_quality_exchange",
    routing_key="anomaly.pm25.critical",
    body=message_body,
    properties=pika.BasicProperties(
        delivery_mode=2,  # Kalıcı mesaj
        content_type='application/json'
    )
)

print("Test anomali mesajı gönderildi!")

# Bağlantıyı kapat
connection.close() 