import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from app.models.air_quality import AirQualityData, AirQualityAnomaly
from app.config import settings
from app.services.database import db
from app.services.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Hava kalitesi verilerinde anomali tespiti yapan servis."""
    
    # WHO standartlarına göre eşik değerleri (μg/m³)
    THRESHOLDS = {
        "pm25": settings.THRESHOLD_PM25,
        "pm10": settings.THRESHOLD_PM10,
        "no2": settings.THRESHOLD_NO2,
        "so2": settings.THRESHOLD_SO2,
        "o3": settings.THRESHOLD_O3
    }
    
    # Anomali şiddet seviyeleri için çarpanlar
    SEVERITY_LEVELS = {
        "low": 1.2,       # %20 aşım
        "medium": 1.5,    # %50 aşım
        "high": 2.0,      # %100 aşım
        "critical": 3.0   # %200 aşım
    }
    
    def __init__(self):
        pass
    
    async def check_threshold_anomaly(self, data: AirQualityData) -> Optional[List[AirQualityAnomaly]]:
        """
        WHO standartlarına göre eşik değerlerini aşan kirlilik seviyelerini tespit eder.
        
        Args:
            data (AirQualityData): Kontrol edilecek hava kalitesi verisi
            
        Returns:
            Optional[List[AirQualityAnomaly]]: Tespit edilen anomaliler listesi, anomali yoksa None
        """
        anomalies = []
        
        # Veri modelindeki kirlilik parametrelerini kontrol et
        for parameter, threshold in self.THRESHOLDS.items():
            value = getattr(data, parameter, None)
            
            if value is not None and value > threshold:
                # Aşım oranını hesapla
                ratio = value / threshold
                
                # Anomali şiddetini belirle
                severity = self._determine_severity(ratio)
                
                # Anomali modelini oluştur
                anomaly = AirQualityAnomaly(
                    data=data,
                    parameter=parameter,
                    threshold=threshold,
                    actual_value=value,
                    detection_method="threshold",
                    severity=severity,
                    detected_at=datetime.utcnow()
                )
                
                anomalies.append(anomaly)
                
                # Loglama yap
                logger.warning(
                    f"Anomali tespit edildi: {parameter.upper()} değeri {value} μg/m³, "
                    f"eşik değer {threshold} μg/m³, şiddet: {severity}, "
                    f"konum: {data.latitude}, {data.longitude}"
                )
        
        return anomalies if anomalies else None
    
    async def check_historical_anomaly(self, data: AirQualityData) -> Optional[List[AirQualityAnomaly]]:
        """
        Son 24 saatlik ortalamaya göre anormal artış gösteren değerleri tespit eder.
        
        Args:
            data (AirQualityData): Kontrol edilecek hava kalitesi verisi
            
        Returns:
            Optional[List[AirQualityAnomaly]]: Tespit edilen anomaliler listesi, anomali yoksa None
        """
        anomalies = []
        
        # Son 24 saatteki verileri getir
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        # Her parametre için kontrol et
        for parameter in ["pm25", "pm10", "no2", "so2", "o3"]:
            value = getattr(data, parameter, None)
            
            if value is None:
                continue
                
            # Parametre için son 24 saatteki verileri getir
            historical_data = await db.get_data_by_parameter(parameter, start_time, end_time)
            
            if not historical_data:
                continue
                
            # Verileri numpy dizisine dönüştür
            values = np.array([doc.get(parameter, 0) for doc in historical_data if parameter in doc])
            
            if len(values) < 10:  # Yeterli veri yok
                continue
                
            # Ortalama ve standart sapma hesapla
            mean = np.mean(values)
            std = np.std(values)
            
            # Z-score hesapla
            if std == 0:  # Standart sapma sıfır ise, tüm değerler aynı
                continue
                
            z_score = (value - mean) / std
            
            # Z-score eşik değeri (3.0 genellikle anormal kabul edilir)
            z_threshold = 3.0
            
            if z_score > z_threshold:
                # Şiddet hesapla (Z-score'a göre)
                severity = self._determine_severity_by_zscore(z_score)
                
                # Anomali modelini oluştur
                anomaly = AirQualityAnomaly(
                    data=data,
                    parameter=parameter,
                    threshold=mean + z_threshold * std,
                    actual_value=value,
                    detection_method="z-score",
                    severity=severity,
                    detected_at=datetime.utcnow()
                )
                
                anomalies.append(anomaly)
                
                # Loglama yap
                logger.warning(
                    f"Z-score anomalisi tespit edildi: {parameter.upper()} değeri {value} μg/m³, "
                    f"ortalama {mean:.2f} μg/m³, Z-score: {z_score:.2f}, şiddet: {severity}, "
                    f"konum: {data.latitude}, {data.longitude}"
                )
        
        return anomalies if anomalies else None
    
    def _determine_severity(self, ratio: float) -> str:
        """
        Eşik değerine göre aşım oranına bakarak anomali şiddetini belirler.
        
        Args:
            ratio (float): Aşım oranı (gerçek değer / eşik değer)
            
        Returns:
            str: Anomali şiddeti (low, medium, high, critical)
        """
        if ratio >= self.SEVERITY_LEVELS["critical"]:
            return "critical"
        elif ratio >= self.SEVERITY_LEVELS["high"]:
            return "high"
        elif ratio >= self.SEVERITY_LEVELS["medium"]:
            return "medium"
        else:
            return "low"
    
    def _determine_severity_by_zscore(self, z_score: float) -> str:
        """
        Z-score değerine göre anomali şiddetini belirler.
        
        Args:
            z_score (float): Z-score değeri
            
        Returns:
            str: Anomali şiddeti (low, medium, high, critical)
        """
        if z_score >= 5.0:
            return "critical"
        elif z_score >= 4.0:
            return "high"
        elif z_score >= 3.5:
            return "medium"
        else:
            return "low"

# Singleton instance
anomaly_detector = AnomalyDetector() 