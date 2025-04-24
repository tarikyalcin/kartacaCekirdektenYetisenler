from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, GEOSPHERE
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from ..config import settings
from ..utils.json_encoder import convert_mongo_document

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def init_db(self):
        try:
            # MongoDB bağlantısı kur
            logging.info(f"MongoDB bağlantısı kuruluyor: {settings.MONGODB_URL}")
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Air Quality Data Collection
            air_quality_collection = self.db.air_quality_data
            await air_quality_collection.create_indexes([
                IndexModel([("location", GEOSPHERE)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("parameter", ASCENDING), ("timestamp", DESCENDING)])
            ])
            
            # Anomalies Collection
            anomalies_collection = self.db.anomalies
            await anomalies_collection.create_indexes([
                IndexModel([("data.location", GEOSPHERE)]),
                IndexModel([("detected_at", DESCENDING)]),
                IndexModel([("parameter", ASCENDING), ("detected_at", DESCENDING)])
            ])
            
            # Locations Collection
            locations_collection = self.db.locations
            await locations_collection.create_indexes([
                IndexModel([("location", GEOSPHERE)]),
                IndexModel([("name", ASCENDING)])
            ])
            
            logging.info("MongoDB bağlantısı ve indeksler başarıyla oluşturuldu")
        except Exception as e:
            logging.error(f"MongoDB bağlantısı kurulamadı: {str(e)}")
            raise

    async def insert_air_quality_data(self, data: dict) -> str:
        """
        Hava kalitesi verisini veritabanına ekler.
        
        Args:
            data (dict): Hava kalitesi verisi dokümanı
        
        Returns:
            str: Eklenen dokümanın ID'si
        """
        result = await self.db.air_quality_data.insert_one(data)
        return str(result.inserted_id)

    async def insert_anomaly(self, data: dict) -> str:
        """
        Anomali verisini veritabanına ekler.
        
        Args:
            data (dict): Anomali verisi dokümanı
        
        Returns:
            str: Eklenen dokümanın ID'si
        """
        result = await self.db.anomalies.insert_one(data)
        return str(result.inserted_id)

    async def get_air_quality_data(self, query: dict, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Belirli kriterlere göre hava kalitesi verilerini getirir.
        
        Args:
            query (dict): MongoDB sorgu dokümanı
            limit (int, optional): Maksimum sonuç sayısı. Varsayılan 100.
        
        Returns:
            List[Dict[str, Any]]: Hava kalitesi verileri listesi
        """
        cursor = self.db.air_quality_data.find(query).sort("timestamp", DESCENDING).limit(limit)
        results = await cursor.to_list(length=limit)
        # ObjectId'leri string'e dönüştür
        return convert_mongo_document(results)

    async def get_anomalies(self, query: dict, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Belirli kriterlere göre anomali verilerini getirir.
        
        Args:
            query (dict): MongoDB sorgu dokümanı
            limit (int, optional): Maksimum sonuç sayısı. Varsayılan 100.
        
        Returns:
            List[Dict[str, Any]]: Anomali verileri listesi
        """
        cursor = self.db.anomalies.find(query).sort("detected_at", DESCENDING).limit(limit)
        results = await cursor.to_list(length=limit)
        # ObjectId'leri string'e dönüştür
        return convert_mongo_document(results)

    async def aggregate_pollution_data(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Kirlilik verilerini aggregate işlemine tabi tutar.
        
        Args:
            pipeline (List[Dict[str, Any]]): MongoDB aggregate pipeline
        
        Returns:
            List[Dict[str, Any]]: Aggregate işlemi sonucu
        """
        cursor = self.db.air_quality_data.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        # ObjectId'leri string'e dönüştür
        return convert_mongo_document(results)
        
    async def get_data_by_parameter(self, parameter: str, start_time: datetime, end_time: datetime, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Belirli bir parametreye göre hava kalitesi verilerini getirir.
        
        Args:
            parameter (str): Hava kalitesi parametresi (pm25, pm10, no2, so2, o3)
            start_time (datetime): Başlangıç zamanı
            end_time (datetime): Bitiş zamanı
            limit (int, optional): Maksimum sonuç sayısı. Varsayılan 100.
        
        Returns:
            List[Dict[str, Any]]: Hava kalitesi verileri listesi
        """
        query = {
            parameter: {"$exists": True},
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }
        cursor = self.db.air_quality_data.find(query).sort("timestamp", DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)

db = Database() 