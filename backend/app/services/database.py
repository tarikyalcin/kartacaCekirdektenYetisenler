from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, GEOSPHERE
from datetime import datetime
from typing import Optional
import os
from ..config import settings

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        
    async def init_db(self):
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
            IndexModel([("location", GEOSPHERE)]),
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("parameter", ASCENDING), ("timestamp", DESCENDING)])
        ])
        
        # Locations Collection
        locations_collection = self.db.locations
        await locations_collection.create_indexes([
            IndexModel([("location", GEOSPHERE)]),
            IndexModel([("name", ASCENDING)])
        ])

    async def insert_air_quality_data(self, data: dict):
        data["timestamp"] = datetime.utcnow()
        return await self.db.air_quality_data.insert_one(data)

    async def insert_anomaly(self, data: dict):
        data["timestamp"] = datetime.utcnow()
        return await self.db.anomalies.insert_one(data)

    async def get_air_quality_data(self, location: dict, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        query = {"location": location}
        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}
        return await self.db.air_quality_data.find(query).sort("timestamp", DESCENDING).to_list(length=1000)

    async def get_anomalies(self, location: dict, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        query = {"location": location}
        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}
        return await self.db.anomalies.find(query).sort("timestamp", DESCENDING).to_list(length=1000)

db = Database() 