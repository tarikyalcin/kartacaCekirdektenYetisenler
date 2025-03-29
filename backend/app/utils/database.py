from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.collection import Collection
from app.config import (
    MONGO_URI, 
    MONGO_DB_NAME, 
    MONGO_COLLECTION_DATA, 
    MONGO_COLLECTION_ANOMALIES
)

# Asenkron MongoDB bağlantısı
async def get_mongo_client():
    """
    MongoDB istemcisi oluşturur.
    
    Returns:
        AsyncIOMotorClient: MongoDB asenkron bağlantı istemcisi
    """
    client = AsyncIOMotorClient(MONGO_URI)
    return client

async def get_database():
    """
    MongoDB veritabanı bağlantısı döndürür.
    
    Returns:
        Database: MongoDB veritabanı
    """
    client = await get_mongo_client()
    return client[MONGO_DB_NAME]

async def get_air_quality_collection():
    """
    Hava kalitesi verileri koleksiyonunu döndürür.
    
    Returns:
        Collection: MongoDB koleksiyonu
    """
    db = await get_database()
    return db[MONGO_COLLECTION_DATA]

async def get_anomalies_collection():
    """
    Anomali verileri koleksiyonunu döndürür.
    
    Returns:
        Collection: MongoDB koleksiyonu
    """
    db = await get_database()
    return db[MONGO_COLLECTION_ANOMALIES]

# Senkron MongoDB bağlantısı (worker için)
def get_sync_mongo_client():
    """
    Senkron MongoDB istemcisi oluşturur.
    
    Returns:
        MongoClient: MongoDB senkron bağlantı istemcisi
    """
    return MongoClient(MONGO_URI)

def get_sync_database():
    """
    Senkron MongoDB veritabanı bağlantısı döndürür.
    
    Returns:
        Database: MongoDB veritabanı
    """
    client = get_sync_mongo_client()
    return client[MONGO_DB_NAME]

def get_sync_air_quality_collection():
    """
    Senkron hava kalitesi verileri koleksiyonunu döndürür.
    
    Returns:
        Collection: MongoDB koleksiyonu
    """
    db = get_sync_database()
    return db[MONGO_COLLECTION_DATA]

def get_sync_anomalies_collection():
    """
    Senkron anomali verileri koleksiyonunu döndürür.
    
    Returns:
        Collection: MongoDB koleksiyonu
    """
    db = get_sync_database()
    return db[MONGO_COLLECTION_ANOMALIES]

async def create_indexes():
    """
    MongoDB koleksiyonları için gerekli indeksleri oluşturur.
    """
    air_quality_collection = await get_air_quality_collection()
    anomalies_collection = await get_anomalies_collection()
    
    # Zaman serisi sorguları için indeks
    await air_quality_collection.create_index("timestamp")
    
    # Coğrafi sorgular için 2dsphere indeksi
    await air_quality_collection.create_index([("location", "2dsphere")])
    
    # Anomali koleksiyonu için indeksler
    await anomalies_collection.create_index("detected_at")
    await anomalies_collection.create_index("parameter")
    await anomalies_collection.create_index([("data.location", "2dsphere")]) 