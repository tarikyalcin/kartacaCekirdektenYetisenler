# Gerçek Zamanlı Hava Kirliliği İzleme Platformu

Bu proje, dünya genelinde hava kirlilik verilerini toplayan, analiz eden ve görselleştiren web tabanlı bir platformdur.

## Teknoloji Seçimleri

- **Backend:** Python (FastAPI)
- **Mimari:** Monolitik
- **Veritabanı:** MongoDB
- **Kuyruklama Sistemi:** RabbitMQ
- **Frontend:** React
- **Harita Kütüphanesi:** Leaflet
- **Grafik Kütüphanesi:** Chart.js

## Özellikler

- Gerçek zamanlı hava kalitesi verilerini toplama ve analiz etme
- Anomali tespiti ve uyarı mekanizması
- Interaktif dünya haritası üzerinde kirlilik seviyelerini görselleştirme
- Kirlilik seviyelerinin zaman içindeki değişimini gösteren grafikler
- WHO limitlerini aşan bölgelerin tespiti ve raporlanması
- WebSocket üzerinden gerçek zamanlı veri iletimi

## Proje Adımları

### 1. Proje Yapısının Oluşturulması
- [x] Proje dizin yapısının kurulması
- [x] Backend için gerekli kütüphanelerin kurulumu
- [x] Frontend için gerekli kütüphanelerin kurulumu
- [x] Docker yapılandırması

### 2. Veritabanı ve Kuyruklama Sisteminin Kurulması
- [x] MongoDB şema tasarımı ve indeksleme
- [x] RabbitMQ kuyruk yapılandırması
- [x] Bağlantı testleri

### 3. Backend Geliştirme
- [x] API endpoints tanımlama
- [x] Veri işleme fonksiyonları
- [x] Anomali tespiti algoritmaları
- [x] WebSocket/SSE yapılandırması

### 4. Frontend Geliştirme
- [x] Ana sayfa düzeni (responsive)
- [x] Harita entegrasyonu (Leaflet)
- [x] Grafik oluşturma (Chart.js)
- [x] API bağlantıları
- [x] Gerçek zamanlı veri görselleştirme

### 5. Test Scriptleri Geliştirme
- [x] Manuel veri girişi scripti
- [x] Otomatik test scripti

### 6. Sistem Entegrasyonu ve Testler
- [x] Backend-Frontend entegrasyonu
- [x] Uçtan uca testler
- [x] Hata ayıklama

### 7. Containerization ve Dağıtım
- [x] Dockerfile optimizasyonu
- [x] Docker-compose tamamlama
- [x] Dağıtım testleri

### 8. Dokümantasyon
- [x] API dokümantasyonu (Swagger/OpenAPI)
- [ ] Kurulum ve kullanım rehberi
- [x] Sorun giderme rehberi

## Kurulum ve Çalıştırma

### Docker ile Çalıştırma

1. Repoyu klonlayın:
   ```
   git clone https://github.com/username/hava-kirliligi-izleme.git
   cd hava-kirliligi-izleme
   ```

2. Docker Compose ile servisleri başlatın:
   ```
   docker-compose up -d
   ```

3. Tarayıcınızda aşağıdaki adreslere erişin:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Dokümantasyonu: http://localhost:8000/docs
   - RabbitMQ Yönetim Paneli: http://localhost:15673 (Kullanıcı adı: admin, Şifre: password)

### Test Scriptlerini Çalıştırma

Örnek veri göndermek için:
```
python test_send_async.py
```

Anomali uyarılarını dinlemek için:
```
python test_listen_anomaly.py
``` 