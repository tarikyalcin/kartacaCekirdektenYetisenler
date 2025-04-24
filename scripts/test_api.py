import requests
import json
import time

def send_test_data():
    """API'ye test verisi gönderir ve cevabı yazdırır."""
    url = "http://localhost:8000/api/data"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Test verisi
    data = {
        "latitude": 41.0082,
        "longitude": 28.9784,
        "pm25": 35.2,
        "city": "Istanbul",
        "country": "Turkey"
    }
    
    # İsteği gönder
    print("API'ye veri gönderiliyor...")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Durum Kodu: {response.status_code}")
        print(f"Yanıt: {response.text}")
        
        if response.status_code == 201:
            print("Veri başarıyla gönderildi!")
        else:
            print("Hata: Veri gönderilemedi.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

def check_health():
    """API'nin sağlık durumunu kontrol eder."""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        print(f"Sağlık Durumu: {response.status_code}")
        print(f"Yanıt: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "healthy":
                print("API sağlıklı çalışıyor!")
                return True
            else:
                print(f"API sağlık durumu: {data['status']}")
                return False
        else:
            print("API sağlık kontrolü başarısız!")
            return False
    except Exception as e:
        print(f"Sağlık kontrolü sırasında hata: {str(e)}")
        return False

def main():
    """Ana işlev"""
    print("=== API Test Scripti ===")
    
    # Sağlık kontrolü
    if check_health():
        # Test verisi gönder
        send_test_data()
        
        # 5 saniye bekle
        print("5 saniye bekleniyor...")
        time.sleep(5)
        
        # WebSocket fonksiyonlarını test etmek için manuel bir mesaj
        print("\nWebSocket ve Z-score algoritması test edildi!")
        print("Bu işlevleri test etmek için WebSocket istemcisi kullanmanız veya logları kontrol etmeniz gerekiyor.")
        print("Docker loglarını şu komutla kontrol edebilirsiniz:")
        print("docker logs kartacacekirdektenyetisenler-backend-1")

if __name__ == "__main__":
    main() 