import requests
import json
from datetime import datetime, timedelta
import random

# API URL'leri
BASE_URL = "http://localhost:8000/api"
DATA_ENDPOINT = f"{BASE_URL}/data"
AIR_QUALITY_ENDPOINT = f"{BASE_URL}/air-quality"
ANOMALIES_ENDPOINT = f"{BASE_URL}/anomalies"
POLLUTION_DENSITY_ENDPOINT = f"{BASE_URL}/pollution-density"

# Test konumları
test_locations = [
    {"city": "Ankara", "country": "Türkiye", "latitude": 39.9334, "longitude": 32.8597},
    {"city": "İstanbul", "country": "Türkiye", "latitude": 41.0082, "longitude": 28.9784},
    {"city": "İzmir", "country": "Türkiye", "latitude": 38.4192, "longitude": 27.1287},
    {"city": "Bursa", "country": "Türkiye", "latitude": 40.1885, "longitude": 29.0610},
    {"city": "Antalya", "country": "Türkiye", "latitude": 36.8969, "longitude": 30.7133}
]

# Rastgele hava kalitesi verisi oluşturma fonksiyonu
def generate_random_air_quality(location, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timestamp": timestamp.isoformat(),
        "pm25": random.uniform(5, 180),  # Bazı anomaliler için yüksek değerler
        "pm10": random.uniform(10, 200),
        "no2": random.uniform(5, 100),
        "so2": random.uniform(1, 50),
        "o3": random.uniform(10, 120),
        "source": "test_api_endpoints.py",
        "city": location["city"],
        "country": location["country"]
    }

# Test verisi gönderme fonksiyonu
def send_test_data(count=20):
    print(f"\n[*] {count} adet test verisi gönderiliyor...")
    
    for i in range(count):
        # Rastgele bir konum seç
        location = random.choice(test_locations)
        
        # Rastgele bir zaman (son 24 saat içinde)
        hours_ago = random.uniform(0, 24)
        timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
        
        # Veriyi oluştur
        data = generate_random_air_quality(location, timestamp)
        
        # API'ye gönder
        response = requests.post(DATA_ENDPOINT, json=data)
        
        # Her 5 veride bir durum raporu
        if i % 5 == 0:
            print(f"  - Veri #{i+1} gönderildi: {location['city']} - Durum: {response.status_code}")
    
    print("[*] Test verileri başarıyla gönderildi!")

# Hava kalitesi endpoint'ini test etme
def test_air_quality_endpoint():
    print("\n[*] Hava kalitesi endpoint'i test ediliyor...")
    
    # Ankara için verileri getir
    ankara = test_locations[0]
    url = f"{AIR_QUALITY_ENDPOINT}/{ankara['latitude']}/{ankara['longitude']}?radius=50"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  - Durum: {response.status_code} OK")
        print(f"  - Toplam {len(data)} veri bulundu")
        if data:
            print(f"  - Örnek veri: {json.dumps(data[0], indent=2)[:200]}...")
    else:
        print(f"  - Hata: {response.status_code} - {response.text}")

# Anomaliler endpoint'ini test etme
def test_anomalies_endpoint():
    print("\n[*] Anomaliler endpoint'i test ediliyor...")
    
    url = f"{ANOMALIES_ENDPOINT}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  - Durum: {response.status_code} OK")
        print(f"  - Toplam {len(data)} anomali bulundu")
        if data:
            print(f"  - Örnek anomali: {json.dumps(data[0], indent=2)[:200]}...")
    else:
        print(f"  - Hata: {response.status_code} - {response.text}")

# Kirlilik yoğunluğu endpoint'ini test etme
def test_pollution_density_endpoint():
    print("\n[*] Kirlilik yoğunluğu endpoint'i test ediliyor...")
    
    url = f"{POLLUTION_DENSITY_ENDPOINT}?parameter=pm25"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  - Durum: {response.status_code} OK")
        print(f"  - Toplam {len(data)} bölge bulundu")
        if data:
            print(f"  - Örnek yoğunluk verisi: {json.dumps(data[0], indent=2)[:200]}...")
    else:
        print(f"  - Hata: {response.status_code} - {response.text}")

# Ana fonksiyon
if __name__ == "__main__":
    print("=== Hava Kalitesi API Endpoint Test Aracı ===")
    
    # Test verisi gönder
    send_test_data(20)
    
    # Endpoint'leri test et
    test_air_quality_endpoint()
    test_anomalies_endpoint()
    test_pollution_density_endpoint()
    
    print("\n[*] Test tamamlandı.") 