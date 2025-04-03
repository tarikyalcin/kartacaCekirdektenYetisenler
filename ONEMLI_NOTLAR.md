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