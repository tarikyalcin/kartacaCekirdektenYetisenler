from fastapi import APIRouter, HTTPException
from app.models.air_quality import AirQualityData, AirQualityAnomaly

router = APIRouter()

# Bu dosya, API endpoint'lerini organize etmek için kullanılacak
# Şu an sadece temel yapı oluşturuluyor, ileride farklı router'lar eklenebilir:
# - data_router.py (veri girişi ve sorgulamaları için)
# - anomaly_router.py (anomali sorgulamaları için)
# - map_router.py (harita görselleştirmesi için) 