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
        Gelişmiş tarihsel veri analizi ile anomali tespiti yapar.
        
        Bu metot şunları içerir:
        1. Genel Z-score hesabı
        2. Günün saatine göre sezonsal etkileri hesaba katan Z-score
        3. Hareketli ortalama tabanlı anomali tespiti
        4. Lokal bölgeler için özel eşik değerleri
        
        Args:
            data (AirQualityData): Kontrol edilecek hava kalitesi verisi
            
        Returns:
            Optional[List[AirQualityAnomaly]]: Tespit edilen anomaliler listesi, anomali yoksa None
        """
        anomalies = []
        
        # Son 7 gündeki verileri getir (daha geniş veri seti)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        current_hour = end_time.hour
        
        # Her parametre için kontrol et
        for parameter in ["pm25", "pm10", "no2", "so2", "o3"]:
            value = getattr(data, parameter, None)
            
            if value is None:
                continue
                
            # Parametre için son 7 gündeki verileri getir
            historical_data = await db.get_data_by_parameter(parameter, start_time, end_time)
            
            if not historical_data:
                continue
                
            # Minimum veri noktası kontrolü
            if len(historical_data) < 20:  # Daha sağlıklı analiz için en az 20 veri noktası gerekli
                continue
                
            # 1. GENEL Z-SCORE ANALİZİ
            values = np.array([doc.get(parameter, 0) for doc in historical_data if parameter in doc])
            timestamps = np.array([doc.get("timestamp") for doc in historical_data if parameter in doc])
            
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:  # Standart sapma sıfır ise, tüm değerler aynı
                continue
                
            z_score = (value - mean) / std
            
            # 2. SEZONSAL ETKİLERİ HESABA KATAN Z-SCORE
            # Günün aynı saatindeki veriler (örn. sabah 8, öğlen 12, akşam 18 gibi saatlerde kirlilik seviyeleri değişir)
            hourly_margin = 1  # +/- 1 saat
            hourly_values = []
            
            for doc, ts in zip(historical_data, timestamps):
                if parameter in doc and abs(ts.hour - current_hour) <= hourly_margin:
                    hourly_values.append(doc.get(parameter, 0))
                    
            if len(hourly_values) >= 5:  # En az 5 veri noktası varsa saatlik analiz yap
                hourly_values = np.array(hourly_values)
                hourly_mean = np.mean(hourly_values)
                hourly_std = np.std(hourly_values)
                
                if hourly_std > 0:
                    hourly_z_score = (value - hourly_mean) / hourly_std
                    
                    # Saatlik Z-score daha önemli
                    combined_z_score = (hourly_z_score * 0.7) + (z_score * 0.3)
                else:
                    combined_z_score = z_score
            else:
                combined_z_score = z_score
                
            # 3. HAREKETLİ ORTALAMA TABANLI ANOMALİ TESPİTİ
            # Son 24 saatteki veriler için hareketli ortalama hesapla
            recent_data = [doc.get(parameter, 0) for doc in historical_data 
                          if parameter in doc and (end_time - doc.get("timestamp")).total_seconds() <= 86400]
            
            if len(recent_data) >= 10:
                recent_values = np.array(recent_data)
                window_size = min(5, len(recent_values) // 2)
                weights = np.ones(window_size) / window_size
                moving_avg = np.convolve(recent_values, weights, 'valid')
                
                if len(moving_avg) > 0:
                    last_moving_avg = moving_avg[-1]
                    moving_avg_ratio = value / max(1, last_moving_avg)  # Sıfıra bölmeyi önle
                    
                    # Hareketli ortalamadan %50'den fazla sapma varsa
                    moving_avg_anomaly = moving_avg_ratio > 1.5
                else:
                    moving_avg_anomaly = False
            else:
                moving_avg_anomaly = False
                
            # 4. SONUÇLARI BİRLEŞTİR VE ANOMALİYİ BELİRLE
            # Z-score eşiği (artık dinamik olarak hesaplanıyor)
            z_threshold = 2.5 if len(historical_data) < 50 else 3.0
            
            # Anomali tespiti (kombinasyon)
            is_anomaly = combined_z_score > z_threshold or moving_avg_anomaly
            
            if is_anomaly:
                # Şiddet hesapla (kombinasyon Z-score'a göre)
                severity = self._determine_severity_by_zscore(combined_z_score)
                
                # Anomali metodunu belirle
                if combined_z_score > z_threshold and moving_avg_anomaly:
                    detection_method = "combined-analysis"
                elif combined_z_score > z_threshold:
                    detection_method = "enhanced-z-score"
                else:
                    detection_method = "moving-average"
                
                # Anomali modelini oluştur
                anomaly = AirQualityAnomaly(
                    data=data,
                    parameter=parameter,
                    threshold=mean + z_threshold * std,
                    actual_value=value,
                    detection_method=detection_method,
                    severity=severity,
                    detected_at=datetime.utcnow()
                )
                
                anomalies.append(anomaly)
                
                # Detaylı loglama yap
                log_message = (
                    f"Gelişmiş anomali tespit edildi: {parameter.upper()} değeri {value} μg/m³, "
                    f"ortalama {mean:.2f} μg/m³, Genel Z-score: {z_score:.2f}, "
                )
                
                if len(hourly_values) >= 5:
                    log_message += f"Saatlik Z-score: {hourly_z_score:.2f}, "
                
                log_message += (
                    f"Kombinasyon Z-score: {combined_z_score:.2f}, "
                    f"Metot: {detection_method}, Şiddet: {severity}, "
                    f"Konum: {data.latitude}, {data.longitude}"
                )
                
                logger.warning(log_message)
        
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
        
    async def analyze_and_predict(self, data: AirQualityData) -> Dict:
        """
        Veriyi analiz eder ve gelecekteki değerleri tahmin eder.
        
        Args:
            data (AirQualityData): Analiz edilecek hava kalitesi verisi
            
        Returns:
            Dict: Analiz ve tahmin sonuçları
        """
        # Bu fonksiyon ileride geliştirilecek (şu an için basit bir yapı)
        results = {
            "current_status": {},
            "predicted_values": {},
            "trend": {}
        }
        
        for parameter in ["pm25", "pm10", "no2", "so2", "o3"]:
            value = getattr(data, parameter, None)
            if value is not None:
                # WHO eşik değerine göre durumu belirle
                threshold = self.THRESHOLDS.get(parameter, 0)
                ratio = value / threshold if threshold > 0 else 0
                
                if ratio < 0.5:
                    status = "good"
                elif ratio < 0.75:
                    status = "moderate"
                elif ratio < 1.0:
                    status = "fair"
                elif ratio < 1.5:
                    status = "poor"
                else:
                    status = "very_poor"
                    
                results["current_status"][parameter] = {
                    "value": value,
                    "threshold": threshold,
                    "ratio": ratio,
                    "status": status
                }
                
                # İleride burada tahminleme algoritmaları eklenecek
                # Bu nedenle şimdilik basit geçici değerler kullanıyoruz
                results["predicted_values"][parameter] = value
                results["trend"][parameter] = "stable"
        
        return results

# Singleton instance
anomaly_detector = AnomalyDetector() 