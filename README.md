# Gerçek Zamanlı Hava Kirliliği İzleme Platformu

Bu proje, dünya genelinde hava kirlilik verilerini toplayan, analiz eden ve görselleştiren web tabanlı bir platformdur. Anomali tespiti, gerçek zamanlı izleme ve interaktif harita görselleştirmesi gibi özellikler sunar.

## Projenin Amacı ve Kapsamı

Sistem, çeşitli bölgelerdeki hava kirliliği verilerini işleyerek kullanıcılara anlamlı bilgiler sunar ve kritik kirlilik seviyelerinde uyarılar verir.

## Teknolojiler ve Mimari

- **Backend:** Python (FastAPI) - Monolitik yapıda
- **Frontend:** React (Leaflet, Chart.js)
- **Veritabanı:** MongoDB
- **Kuyruklama:** RabbitMQ
- **Anomali Tespiti:** Eşik değeri kontrolü, Z-score analizi, coğrafi karşılaştırma

Veri Akışı: API → RabbitMQ → İşleme Servisi → MongoDB → Frontend

## Kurulum ve Çalıştırma

### Docker ile Çalıştırma (Önerilen)

1. Repoyu klonlayın:
   ```
   git clone https://github.com/[kullanici-adi]/kartacaCekirdektenYetisenler.git
   cd kartacaCekirdektenYetisenler
   ```

2. Docker Compose ile çalıştırın:
   ```
   docker-compose up -d
   ```

3. Erişim adresleri:
   - Frontend: http://localhost:4000
   - Backend API: http://localhost:8000
   - API Dokümantasyonu: http://localhost:8000/docs
   - RabbitMQ Yönetim Paneli: http://localhost:15673 (Kullanıcı: admin, Şifre: password)

## Test Scriptleri

### Veri Gönderme

```bash
python test_send_async.py
```

### Manuel Veri Girişi

```bash
# Linux/Mac
./manual-input.sh 39.9334 32.8597 pm25 75.3 Ankara Türkiye

# Windows PowerShell
.\manual-input.ps1 -latitude 39.9334 -longitude 32.8597 -parameter pm25 -value 75.3 -city Ankara -country Türkiye
```

### Otomatik Test

```bash
# Linux/Mac
./auto-test.sh --duration=300 --rate=2 --anomaly-chance=30

# Windows PowerShell
.\auto-test.ps1 -Duration 300 -Rate 2 -AnomalyChance 30
```

## API Özeti

API dokümantasyonu için Swagger UI: `http://localhost:8000/docs`

- `POST /api/data` - Hava kalitesi verisi gönderme
- `GET /api/air-quality/{lat}/{lon}` - Belirli konum için veri alma
- `GET /api/anomalies` - Anomalileri listeleme
- `GET /api/pollution-density` - Coğrafi bölgeye göre kirlilik yoğunluğu
- `GET /api/health` - Sistem sağlık durumu

## Sorun Giderme

- **Docker sorunları:** `docker logs [konteyner-adı]` ile logları kontrol edin
- **Veri görünmüyor:** Veritabanına örnek veri eklemek için `python scripts/add_real_city_data.py` çalıştırın
- **Port çakışması:** Kullanılan portların (4000, 8000, 27017, 5673, 15673) müsait olduğunu kontrol edin
- **Frontend harita sorunları:** Tarayıcı konsolunu ve API bağlantısını kontrol edin

## Anomali Tespiti Eşik Değerleri

- PM2.5: > 25 μg/m³
- PM10: > 50 μg/m³
- NO2: > 40 μg/m³
- SO2: > 20 μg/m³
- O3: > 100 μg/m³

Daha detaylı bilgi için lütfen `KURULUM_VE_CALISTIRMA.md` dosyasına bakın. 