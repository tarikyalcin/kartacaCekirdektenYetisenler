# 🔑 Önemli Notlar ve Bağlantı Bilgileri

## MongoDB Atlas Bilgileri
- Veritabanı Adı: `air_quality_monitoring`
- Koleksiyonlar:
  - `air_quality_data`: Ham hava kalitesi verileri
  - `anomalies`: Tespit edilen anormal değerler
  - `locations`: Konum bilgileri
- Bağlantı URL'i:
```
mongodb+srv://tarikyalcinwork:NVuuGYILCxf0YIyS@air-quality-monitoring.jq3rc.mongodb.net/?retryWrites=true&w=majority&appName=air-quality-monitoring
```

## RabbitMQ Bilgileri
- Yönetim Arayüzü: http://localhost:15673
- AMQP Port: 5673
- Kullanıcı Adı: admin
- Şifre: password

## Proje Yapısı
- Backend: Python (FastAPI)
- Veritabanı: MongoDB Atlas (Cloud)
- Mesaj Kuyruğu: RabbitMQ (Docker)

## Docker Komutları
- Containerları başlatma: `docker-compose up -d`
- Containerları durdurma: `docker-compose down`
- Container durumunu görme: `docker ps`

## Önemli Kontrol Noktaları
1. MongoDB Atlas'ta veritabanı ve koleksiyonların varlığı
2. RabbitMQ yönetim arayüzüne erişim
3. Docker containerlarının çalışır durumda olması

## Yapılandırma Dosyaları
- `docker-compose.yml`: Container yapılandırmaları
- `backend/.env`: Ortam değişkenleri ve bağlantı bilgileri

# Önemli Notlar

Bu dosya, proje geliştirme sürecinde dikkat edilmesi gereken önemli noktaları ve sonraki adımlar için hatırlatmaları içermektedir.

## Docker ve Konteyner Yönetimi

1. **Konteyner Başlatma Sırası**:
   - MongoDB ve RabbitMQ önce başlatılmalı, backend servisi bu servislere bağımlı.
   - Docker Compose `depends_on` özelliği sadece başlatma sırasını belirler, servisin hazır olmasını beklemez.
   - Bu nedenle backend kodunda uygun bekleme ve yeniden deneme mekanizmaları uygulanmıştır.

2. **Veri Kalıcılığı**:
   - MongoDB verilerinin kalıcı olması için volume tanımlanmıştır.
   - Docker konteynerleri yeniden başlatıldığında veriler korunacaktır.

3. **Docker Compose Uyarısı**:
   ```
   docker-compose.yml: the attribute 'version' is obsolete, it will be ignored, please remove it
   ```
   - Yeni Docker Compose sürümlerinde `version` özniteliği artık kullanılmamaktadır. Gelecekte kaldırılabilir.

## Veritabanı ve Mesajlaşma

1. **MongoDB Bağlantısı**:
   - Uygulamanın MongoDB'ye bağlantısı `mongodb://admin:password@mongodb:27017/air_quality_db?authSource=admin` adresi üzerinden yapılmaktadır.
   - İndeksler otomatik olarak oluşturulmaktadır:
     - `location` alanı için 2dsphere indeksi (coğrafi sorgular için)
     - `timestamp` alanı için indeks (zaman sorguları için)

2. **RabbitMQ Kuyrukları**:
   - **raw_data**: Ham verilerin işlenmek üzere alındığı kuyruk
   - **processed_data**: İşlenmiş verilerin iletildiği kuyruk
   - **anomaly_notifications**: Anomali bildirimlerinin gönderildiği kuyruk

3. **Mesaj Serileştirme**:
   - RabbitMQ mesajları JSON formatında serileştirilmektedir.
   - Özel veri tipleri (datetime, ObjectId vb.) için `CustomJSONEncoder` kullanılmaktadır.

## Hata Yönetimi ve Dayanıklılık

1. **Bağlantı Hatalarına Karşı Dayanıklılık**:
   - Her iki servis (MongoDB, RabbitMQ) için bağlantı yeniden deneme mantığı uygulanmıştır.
   - MongoDB için 3 deneme, RabbitMQ için 5 deneme yapılmaktadır.
   - Her denemede artan bekleme süreleri uygulanmaktadır (backoff stratejisi).

2. **Kısmi Çalışma Modu**:
   - Eğer RabbitMQ bağlantısı kurulamazsa, sistem MongoDB ile kısıtlı işlevsellikle çalışabilir.
   - Worker servis, bağımlı olduğu servisler hazır değilse başlatılmaz.

3. **Sağlık Kontrolü**:
   - `/health` endpoint'i tüm sistemin durumunu gerçek zamanlı olarak raporlar.
   - Herhangi bir servis çalışmıyorsa "degraded" durumu bildirilir.

## Anomali Tespiti

1. **Eşik Değeri Kontrolleri**:
   - WHO standartlarına göre belirlenen eşik değerleri `config.py` dosyasında tanımlanmıştır.
   - PM2.5 için eşik değeri 25 μg/m³ olarak belirlenmiştir.

2. **Anomali Şiddeti**:
   - Anomaliler "low", "medium", "high", "critical" şiddetlerinde kategorize edilir.
   - Şiddet, eşik değerinin ne kadar aşıldığı ile belirlenir.

## API Yapısı

1. **Mevcut Endpoint'ler**:
   - `GET /`: Ana sayfa, API'ye hoş geldiniz mesajı
   - `GET /health`: Sağlık durumu kontrolü
   - `POST /api/data`: Yeni veri eklemek için endpoint

2. **Eksik Endpoint'ler (Geliştirilmesi Gerekenler)**:
   - Belirli bir konum için veri getiren endpoint
   - Anomalileri listeleyen endpoint
   - Coğrafi bölgeye göre kirlilik yoğunluğunu getiren endpoint

## Sonraki Adımlar

1. **Eksik API Endpoint'lerinin Tamamlanması**:
   - Verileri sorgulamak ve filtrelemek için GET endpoint'lerinin eklenmesi
   - Coğrafi sorguların desteklenmesi

2. **Frontend Geliştirme**:
   - React veya Vue.js ile kullanıcı arayüzünün geliştirilmesi
   - Harita entegrasyonu (Mapbox veya Leaflet)
   - Kirlilik seviyelerini göstermek için grafikler

3. **Veri Besleme ve Test Scriptleri**:
   - Manuel veri girişi script'i
   - Otomatik test script'i
   - Anomali senaryoları oluşturma mekanizması

4. **Dokümantasyon**:
   - README dosyasının tamamlanması
   - API dokümantasyonunun hazırlanması
   - Kurulum ve kullanım kılavuzlarının oluşturulması 