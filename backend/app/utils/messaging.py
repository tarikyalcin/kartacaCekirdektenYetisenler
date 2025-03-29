import json
import pika
from app.config import (
    RABBITMQ_HOST, 
    RABBITMQ_PORT, 
    RABBITMQ_USER, 
    RABBITMQ_PASS, 
    RABBITMQ_VHOST,
    QUEUE_RAW_DATA,
    QUEUE_PROCESSED_DATA,
    QUEUE_ANOMALIES
)

def get_rabbitmq_connection():
    """
    RabbitMQ bağlantısı oluşturur.
    
    Returns:
        pika.BlockingConnection: RabbitMQ bağlantısı
    """
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def get_channel(connection=None):
    """
    RabbitMQ kanalı oluşturur.
    
    Args:
        connection (pika.BlockingConnection, optional): Mevcut bağlantı. 
            Eğer None ise yeni bağlantı oluşturulur.
    
    Returns:
        pika.channel.Channel: RabbitMQ kanalı
    """
    if connection is None:
        connection = get_rabbitmq_connection()
    
    channel = connection.channel()
    
    # Kuyrukları tanımla
    channel.queue_declare(queue=QUEUE_RAW_DATA, durable=True)
    channel.queue_declare(queue=QUEUE_PROCESSED_DATA, durable=True)
    channel.queue_declare(queue=QUEUE_ANOMALIES, durable=True)
    
    return channel

def publish_message(queue_name, message, channel=None):
    """
    Belirtilen kuyruğa mesaj gönderir.
    
    Args:
        queue_name (str): Mesajın gönderileceği kuyruk adı
        message (dict): Gönderilecek mesaj (JSON'a dönüştürülecek)
        channel (pika.channel.Channel, optional): Mevcut kanal. 
            Eğer None ise yeni kanal oluşturulur.
    """
    connection = None
    should_close_channel = False
    
    try:
        if channel is None:
            connection = get_rabbitmq_connection()
            channel = get_channel(connection)
            should_close_channel = True
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Kalıcı mesaj
                content_type='application/json'
            )
        )
    finally:
        if should_close_channel and connection:
            connection.close() 