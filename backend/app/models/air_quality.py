from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from geopy.distance import geodesic


class GeoLocation(BaseModel):
    """Coğrafi konum için model"""
    type: str = Field(default="Point", description="GeoJSON tipi")
    coordinates: List[float] = Field(..., description="[longitude, latitude] formatında koordinatlar")


class AirQualityData(BaseModel):
    """Bir lokasyondaki hava kalitesi verisi için model"""
    
    latitude: float = Field(..., ge=-90, le=90, description="Enlem değeri")
    longitude: float = Field(..., ge=-180, le=180, description="Boylam değeri")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Ölçüm zamanı (UTC)")
    
    # Kirlilik parametreleri (μg/m³ cinsinden)
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 değeri (μg/m³)")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 değeri (μg/m³)")
    no2: Optional[float] = Field(None, ge=0, description="NO2 değeri (μg/m³)")
    so2: Optional[float] = Field(None, ge=0, description="SO2 değeri (μg/m³)")
    o3: Optional[float] = Field(None, ge=0, description="O3 değeri (μg/m³)")
    
    # Ek bilgiler
    source: Optional[str] = Field(None, description="Veri kaynağı")
    city: Optional[str] = Field(None, description="Şehir ismi")
    country: Optional[str] = Field(None, description="Ülke ismi")
    
    @validator('timestamp', pre=True)
    def ensure_utc_datetime(cls, v):
        """Tarih değerinin UTC formatında olmasını sağlar"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    def to_mongo_document(self):
        """
        MongoDB dokümanı oluşturur.
        
        Returns:
            dict: MongoDB doküman formatında veri
        """
        doc = self.dict(exclude_none=True)
        
        # MongoDB için GeoJSON formatında konum ekle
        doc["location"] = {
            "type": "Point",
            "coordinates": [self.longitude, self.latitude]
        }
        
        return doc
    
    def distance_to(self, other_lat: float, other_lon: float) -> float:
        """
        Bu nokta ile verilen koordinat arasındaki mesafeyi kilometre cinsinden hesaplar.
        
        Args:
            other_lat (float): Diğer noktanın enlemi
            other_lon (float): Diğer noktanın boylamı
            
        Returns:
            float: İki nokta arasındaki mesafe (km)
        """
        return geodesic((self.latitude, self.longitude), (other_lat, other_lon)).kilometers


class AirQualityAnomaly(BaseModel):
    """Hava kalitesi anomalisi için model"""
    
    data: AirQualityData
    parameter: str = Field(..., description="Anomali tespit edilen parametre (pm25, pm10, no2, so2, o3)")
    threshold: float = Field(..., description="Anomali eşik değeri")
    actual_value: float = Field(..., description="Ölçülen gerçek değer")
    detection_method: str = Field(..., description="Anomali tespit metodu (threshold, z-score, vb.)")
    severity: str = Field(..., description="Anomali şiddeti (low, medium, high, critical)")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Anomali tespit zamanı")
    
    def to_mongo_document(self):
        """
        MongoDB dokümanı oluşturur.
        
        Returns:
            dict: MongoDB doküman formatında veri
        """
        doc = self.dict(exclude={"data"})
        data_doc = self.data.to_mongo_document()
        doc["data"] = data_doc
        return doc 