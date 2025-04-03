import aio_pika
import json
from typing import Callable, Dict, Any
from ..config import settings

class RabbitMQ:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queues = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "air_quality",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

    async def setup_queues(self):
        # Raw data queue
        raw_data_queue = await self.channel.declare_queue(
            "raw_data",
            durable=True
        )
        await raw_data_queue.bind(self.exchange, "data.raw")

        # Anomaly detection queue
        anomaly_queue = await self.channel.declare_queue(
            "anomaly_detection",
            durable=True
        )
        await anomaly_queue.bind(self.exchange, "data.anomaly")

        # Notification queue
        notification_queue = await self.channel.declare_queue(
            "notifications",
            durable=True
        )
        await notification_queue.bind(self.exchange, "notification.*")

        self.queues = {
            "raw_data": raw_data_queue,
            "anomaly_detection": anomaly_queue,
            "notifications": notification_queue
        }

    async def publish(self, routing_key: str, message: Dict[str, Any]):
        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json"
            ),
            routing_key=routing_key
        )

    async def consume(self, queue_name: str, callback: Callable):
        queue = self.queues[queue_name]
        await queue.consume(callback)

    async def close(self):
        if self.connection:
            await self.connection.close()

rabbitmq = RabbitMQ() 