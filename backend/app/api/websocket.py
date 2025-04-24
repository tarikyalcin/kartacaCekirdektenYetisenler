from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timedelta
from app.services.database import db
from app.services.rabbitmq import rabbitmq
from app.services.anomaly_detection import anomaly_detector
import json
from pydantic import BaseModel, Field
from bson import ObjectId

logger = logging.getLogger(__name__)

# WebSocket bağlantılarını yönetmek için manager sınıfı
class ConnectionManager:
    def __init__(self):
        # Tüm aktif bağlantılar
        self.active_connections: Dict[str, List[WebSocket]] = {
            "air_quality": [],     # Hava kalitesi verileri için bağlantılar
            "anomalies": [],       # Anomali bildirimleri için bağlantılar
            "map_data": []         # Harita verisi için bağlantılar
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
            logger.info(f"Yeni WebSocket bağlantısı ({channel}): {websocket.client.host}")
        else:
            await websocket.close(code=1003, reason=f"Bilinmeyen kanal: {channel}")
            logger.warning(f"Bilinmeyen kanala bağlantı isteği: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
                logger.info(f"WebSocket bağlantısı kapandı ({channel}): {websocket.client.host}")
            except ValueError:
                pass
    
    async def broadcast(self, message: Any, channel: str):
        """Belirli bir kanaldaki tüm bağlantılara mesaj gönderir"""
        if channel not in self.active_connections:
            return
            
        if isinstance(message, dict) or isinstance(message, list):
            message_json = json.dumps(message)
        else:
            message_json = str(message)
            
        # İlgili kanaldaki tüm bağlantılara mesajı gönder
        disconnected_ws = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"WebSocket mesajı gönderilirken hata: {str(e)}")
                disconnected_ws.append(connection)
        
        # Hata alınan bağlantıları kaldır
        for ws in disconnected_ws:
            try:
                self.active_connections[channel].remove(ws)
            except ValueError:
                pass
    
    def get_connection_count(self, channel: str = None) -> Dict[str, int]:
        """Aktif bağlantı sayısını döndürür"""
        if channel:
            if channel in self.active_connections:
                return {channel: len(self.active_connections[channel])}
            return {channel: 0}
        else:
            return {k: len(v) for k, v in self.active_connections.items()}

# Manager oluştur
manager = ConnectionManager()

# WebSocket Router
websocket_router = APIRouter()

@websocket_router.websocket("/ws/air-quality")
async def websocket_air_quality(websocket: WebSocket):
    """Hava kalitesi verilerini gerçek zamanlı takip etmek için WebSocket"""
    await manager.connect(websocket, "air_quality")
    try:
        while True:
            # İstemciden gelen mesajları bekle (isteğe bağlı filtreleme yapabilmek için)
            data = await websocket.receive_text()
            try:
                # İstemciden gelen filtreleri işle
                message = json.loads(data)
                filters = message.get("filters", {})
                
                # Filtrelere göre son verileri getir
                query = {}
                limit = filters.get("limit", 20)
                
                if "parameter" in filters and filters["parameter"]:
                    query[filters["parameter"]] = {"$exists": True}
                
                if "start_time" in filters and filters["start_time"]:
                    start_time = datetime.fromisoformat(filters["start_time"])
                    if "end_time" in filters and filters["end_time"]:
                        end_time = datetime.fromisoformat(filters["end_time"])
                    else:
                        end_time = datetime.utcnow()
                    
                    query["timestamp"] = {"$gte": start_time, "$lte": end_time}
                else:
                    # Varsayılan olarak son 1 saatteki verileri getir
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(hours=1)
                    query["timestamp"] = {"$gte": start_time, "$lte": end_time}
                
                # Filtrelere göre verileri getir
                results = await db.get_air_quality_data(query, limit)
                
                # İstemciye verilerti gönder
                await websocket.send_json({
                    "type": "air_quality_data",
                    "data": results,
                    "timestamp": datetime.utcnow().isoformat(),
                    "count": len(results)
                })
                
            except json.JSONDecodeError:
                logger.error(f"WebSocket mesajı JSON formatında değil: {data}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Geçersiz JSON formatı"
                })
            except Exception as e:
                logger.error(f"WebSocket veri işlenirken hata: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"İşlem hatası: {str(e)}"
                })
            
            # Her istek arasında kısa bir süre bekle (rate limiting)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "air_quality")
    except Exception as e:
        logger.error(f"WebSocket bağlantısında hata: {str(e)}")
        manager.disconnect(websocket, "air_quality")

@websocket_router.websocket("/ws/anomalies")
async def websocket_anomalies(websocket: WebSocket):
    """Anomali bildirimleri için WebSocket"""
    await manager.connect(websocket, "anomalies")
    try:
        # İlk bağlantıda mevcut anomalileri gönder
        query = {
            "detected_at": {
                "$gte": datetime.utcnow() - timedelta(hours=24)
            }
        }
        recent_anomalies = await db.get_anomalies(query, 50)
        
        await websocket.send_json({
            "type": "initial_anomalies",
            "data": recent_anomalies,
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(recent_anomalies)
        })
        
        # Bağlantı açık kaldığı sürece bekle
        while True:
            try:
                # İstemciden mesaj bekle (ping için)
                data = await websocket.receive_text()
                # Heartbeat cevabı gönder
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"WebSocket mesajı alınırken hata: {str(e)}")
                await asyncio.sleep(30)  # Hata durumunda bekle
    except WebSocketDisconnect:
        manager.disconnect(websocket, "anomalies")
    except Exception as e:
        logger.error(f"WebSocket bağlantısında hata: {str(e)}")
        manager.disconnect(websocket, "anomalies")

@websocket_router.websocket("/ws/map-data")
async def websocket_map_data(websocket: WebSocket):
    """Harita görselleştirmesi için gerçek zamanlı veri"""
    await manager.connect(websocket, "map_data")
    try:
        while True:
            try:
                # İstemciden gelen filtreleri al
                data = await websocket.receive_text()
                message = json.loads(data)
                
                parameter = message.get("parameter", "pm25")
                time_window = message.get("time_window", "1h")
                
                # Zaman penceresi seçimi
                end_time = datetime.utcnow()
                if time_window == "1h":
                    start_time = end_time - timedelta(hours=1)
                elif time_window == "24h":
                    start_time = end_time - timedelta(days=1)
                elif time_window == "7d":
                    start_time = end_time - timedelta(days=7)
                else:
                    start_time = end_time - timedelta(hours=1)  # Varsayılan
                
                # Harita verisi için aggregate pipeline oluştur
                pipeline = [
                    {
                        "$match": {
                            parameter: {"$exists": True},
                            "timestamp": {"$gte": start_time, "$lte": end_time}
                        }
                    },
                    {
                        "$group": {
                            "_id": "$location",
                            "avg_value": {"$avg": f"${parameter}"},
                            "max_value": {"$max": f"${parameter}"},
                            "latest": {"$max": "$timestamp"},
                            "count": {"$sum": 1},
                            "latitude": {"$first": "$latitude"},
                            "longitude": {"$first": "$longitude"},
                            "city": {"$first": "$city"},
                            "country": {"$first": "$country"}
                        }
                    }
                ]
                
                # Verileri getir
                results = await db.aggregate_pollution_data(pipeline)
                
                # Sonuçları istemciye gönder
                await websocket.send_json({
                    "type": "map_data",
                    "parameter": parameter,
                    "time_window": time_window,
                    "data": results,
                    "timestamp": datetime.utcnow().isoformat(),
                    "count": len(results)
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Geçersiz JSON formatı"
                })
            except Exception as e:
                logger.error(f"Harita verisi hazırlanırken hata: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            
            await asyncio.sleep(5)  # Her güncelleme arasında 5 saniye bekle
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "map_data")
    except Exception as e:
        logger.error(f"WebSocket bağlantısında hata: {str(e)}")
        manager.disconnect(websocket, "map_data")

@websocket_router.get("/ws/stats")
async def get_websocket_stats():
    """WebSocket bağlantı istatistiklerini döndürür"""
    stats = manager.get_connection_count()
    return {
        "active_connections": stats,
        "total_connections": sum(stats.values())
    }

# RabbitMQ'dan gelen anomali bildirimlerini dinlemek için task
async def listen_for_anomalies():
    """RabbitMQ'dan anomali bildirimlerini dinler ve WebSocket üzerinden yayınlar"""
    logger.info("Anomali dinleme görevi başlatıldı")
    # Başlangıçta RabbitMQ bağlantısının hazır olması için bekle
    await asyncio.sleep(5)
    
    while True:
        try:
            # Anomali bildirimlerini doğrudan RabbitMQ'dan al
            try:
                # RabbitMQ bağlantısı ve kuyruk kontrolü
                if not rabbitmq.connection or not rabbitmq.channel:
                    logger.warning("RabbitMQ bağlantısı hazır değil. Yeniden denenecek...")
                    await asyncio.sleep(5)
                    continue
                
                # Kuyruklar hazır mı kontrol et
                if "anomaly_notifications" not in rabbitmq.queues:
                    logger.warning("Anomali kuyruğu bulunamadı. Yeniden denenecek...")
                    # Kuyrukları yeniden oluşturmayı dene
                    try:
                        await rabbitmq.setup_exchanges_and_queues()
                    except Exception as e:
                        logger.error(f"Kuyruklar oluşturulurken hata: {str(e)}")
                    await asyncio.sleep(5)
                    continue
                
                # Kuyruk nesnesini al
                queue = rabbitmq.queues["anomaly_notifications"]
                
                # Mesaj alma işlemini güvenli bir şekilde yap
                try:
                    # aio_pika kütüphanesini doğrudan kullan
                    message = await queue.get(fail=False)
                    if message:
                        # Mesajı ack'le
                        await message.ack()
                        
                        # Mesaj içeriğini parse et
                        message_body = message.body.decode()
                        data = json.loads(message_body)
                        
                        # WebSocket üzerinden yayınla (ObjectId'leri string'e dönüştür)
                        message_json = json.dumps(data, default=lambda o: str(o) if isinstance(o, ObjectId) else o)
                        parsed_data = json.loads(message_json)
                        
                        # WebSocket üzerinden yayınla
                        await manager.broadcast({
                            "type": "new_anomaly",
                            "data": parsed_data,
                            "timestamp": datetime.utcnow().isoformat()
                        }, "anomalies")
                        
                        # Harita verisi güncelleme sinyali
                        await manager.broadcast({
                            "type": "map_update_needed",
                            "source": "anomaly",
                            "parameter": data.get("parameter"),
                            "timestamp": datetime.utcnow().isoformat()
                        }, "map_data")
                        
                        logger.info(f"Anomali mesajı WebSocket üzerinden yayınlandı: {data.get('parameter')}")
                except Exception as e:
                    logger.error(f"Mesaj alınırken/işlenirken hata: {str(e)}")
            except Exception as e:
                logger.error(f"Anomali mesajı alınırken hata: {str(e)}")
            
            # Kısa bir süre bekle
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Anomali dinleme sırasında hata: {str(e)}")
            await asyncio.sleep(5)  # Hata durumunda daha uzun bekle

# Uygulama başlangıcında anomali dinleme görevini başlat
@websocket_router.on_event("startup")
async def start_anomaly_listener():
    asyncio.create_task(listen_for_anomalies()) 