# Gerçek Zamanlı Hava Kirliliği İzleme Platformu - Yol Haritası

## Teknoloji Seçimleri

- **Backend:** Python (FastAPI) - Hızlı geliştirme, kolay öğrenme eğrisi ve güçlü performans ✅
- **Mimari:** Monolitik (başlangıç için daha basit, daha az karmaşıklık) ✅
- **Veritabanı:** MongoDB (esnek şema, zaman serisi koleksiyonları için destek) ✅
- **Kuyruklama Sistemi:** RabbitMQ (kurulumu ve kullanımı daha kolay) ✅
- **Frontend:** React (geniş ekosistem ve hazır komponentler)
- **Harita Kütüphanesi:** Leaflet (açık kaynak ve kullanımı kolay)
- **Grafik Kütüphanesi:** Chart.js (basit ve kullanımı kolay)

## Detaylı Yol Haritası

### 1. Proje Yapısının Oluşturulması ✅

#### Backend (FastAPI):
- [x] Proje dizin yapısının oluşturulması
- [x] Gerekli kütüphanelerin kurulumu (FastAPI, pika, pymongo, pandas)
- [x] Temel API yapısının kurulması
- [x] Veritabanı ve kuyruklama bağlantılarının yapılandırılması

#### Frontend (React):
- [ ] Create React App ile proje oluşturma
- [ ] Gerekli kütüphanelerin kurulumu (leaflet, chart.js, axios, socket.io-client)
- [ ] Temel sayfa yapısının ve komponentlerin planlanması

#### Docker:
- [x] Backend için Dockerfile oluşturma
- [ ] Frontend için Dockerfile oluşturma
- [x] Docker-compose.yml oluşturma (MongoDB, RabbitMQ, Backend, Frontend)

### 2. Veritabanı ve Kuyruklama Sisteminin Kurulması ✅

#### MongoDB:
- [x] Veritabanı ve koleksiyon yapısının tasarımı
- [x] Zaman serisi koleksiyonlarının oluşturulması
- [x] İndeksleme stratejisinin belirlenmesi
- [x] Coğrafi sorgular için indekslerin yapılandırılması

#### RabbitMQ:
- [x] Kuyruk yapılandırması
- [x] Exchange ve binding tanımları
- [x] Mesaj formatı belirleme

### 3. Backend Geliştirme ✅

#### API Endpoints:
- [x] Veri alma endpoint'i (`/api/data`) - POST
- [x] Belirli bir konum için hava kalitesi verileri getiren endpoint (`/api/air-quality/{location}`)
- [x] Belirli bir zaman aralığında tespit edilen anomalileri listeleyen endpoint (`/api/anomalies`)
- [x] Coğrafi bölgeye göre kirlilik yoğunluğunu getiren endpoint (`/api/pollution-density`)

#### Veri İşleme:
- [x] RabbitMQ'dan mesajları alma ve işleme
- [x] Anomali tespiti algoritmaları (threshold değerleri)
- [x] Tarihsel anomali tespiti için Z-score algoritmasının iyileştirilmesi
- [x] İşlenmiş verileri MongoDB'ye kaydetme
- [x] WebSocket veya SSE ile gerçek zamanlı uyarılar gönderme

### 4. Frontend Geliştirme 🔴

#### Arayüz Komponentleri:
- [ ] Ana sayfa düzeni (responsive)
- [ ] Dünya haritası üzerinde kirlilik seviyelerini gösteren ısı haritası (Leaflet)
- [ ] Kirlilik seviyelerinin zamana göre değişimini gösteren grafikler (Chart.js)
- [ ] Anormal değerler için uyarı paneli
- [ ] Belirli bir bölge seçerek detaylı analiz görüntüleme ekranı

#### API Entegrasyonu:
- [ ] Backend API'leri ile iletişim (Axios)
- [ ] WebSocket veya SSE ile gerçek zamanlı veri alma
- [ ] Veri işleme ve görselleştirme

### 5. Test Scriptleri Geliştirme ✅

#### Manuel Veri Girişi Script'i:
- [x] Bash script oluşturma (`manual-input.sh`)
- [x] API ile iletişim kurma
- [x] Parametreleri doğrulama ve işleme

#### Otomatik Test Script'i:
- [x] Bash script oluşturma (`auto-test.sh`)
- [x] Rastgele konum ve kirlilik değerleri oluşturma
- [x] Anomali senaryoları oluşturma
- [x] İstek oranı ve çalışma süresi kontrolleri

### 6. Sistemin Entegrasyonu ve Testleri ✅

- [x] Backend ve veritabanı entegrasyonu
- [x] Backend ve mesajlaşma sistemi entegrasyonu
- [ ] Frontend ve backend entegrasyonu
- [x] Backend uçtan uca testleri
- [x] Anomali tespiti testleri
- [ ] Frontend testleri
- [x] Hata yönetimi ve dayanıklılık testleri

### 7. Containerization ve Dağıtım ✅

- [x] Backend için Dockerfile optimize edilmesi
- [x] Docker-compose yapılandırmasının tamamlanması
- [x] MongoDB ve RabbitMQ konteynerlerinin yapılandırılması
- [x] Ortam değişkenlerinin yapılandırılması
- [x] Docker container başlatma ve durdurma testleri

### 8. Dokümantasyon 🟡

- [x] Hata çözümleri dokümantasyonu
- [x] Önemli notlar dokümantasyonu
- [x] Yol haritası ve ilerleme durumu
- [ ] README dosyasının hazırlanması
- [ ] API dokümantasyonu (Swagger/OpenAPI)
- [ ] Kurulum ve kullanım rehberi
- [ ] Sorun giderme rehberi

## Sistem Mimarisi ve Veri Akışı

### Veri Girişi: ✅
- Test scriptleri veya API isteği ile veri backend'e gönderilir.
- POST `/api/data` endpoint'i veriyi alır ve RabbitMQ'ya iletir.

### Veri İşleme: ✅
- Worker RabbitMQ'dan `raw_data` kuyruğundan veriyi alır.
- Veri doğrulanır ve MongoDB'ye kaydedilir.
- Anomali tespiti algoritmaları çalıştırılır (threshold ve Z-score).
- Anomali tespit edilirse, anomali bilgileri MongoDB'ye kaydedilir.
- İşlenmiş veri `processed_data` kuyruğuna, anomali bildirimleri `anomaly_notifications` kuyruğuna gönderilir.

### Veri Sorgulama ve İzleme: ✅
- GET endpoint'leri ile veriler sorgulanabilir.
- Sağlık durumu `/health` endpoint'i ile izlenebilir.

## Yapılan Geliştirmeler

### Backend: ✅
- [x] FastAPI ile temel API yapısı oluşturuldu
- [x] MongoDB bağlantısı ve indeksleme
- [x] RabbitMQ entegrasyonu ve kuyruk yapılandırması
- [x] Veri modelleri ve doğrulama (Pydantic)
- [x] Anomali tespiti algoritmaları
- [x] Hata yönetimi ve dayanıklılık iyileştirmeleri
- [x] Sağlık kontrolü ve izleme endpoint'leri
- [x] WebSocket üzerinden gerçek zamanlı veri iletimi
- [x] ObjectId serileştirme sorunları çözüldü

### Docker: ✅
- [x] MongoDB, RabbitMQ ve Backend servisleri için Docker Compose
- [x] Volume yapılandırması (veri kalıcılığı)
- [x] Ağ yapılandırması ve port eşlemeleri

### Test Scriptleri: ✅
- [x] Manuel mesaj gönderme scriptleri (test_send_anomaly.py, test_send_async.py)
- [x] Otomatik dinleyici scriptleri (test_listen_anomaly.py, test_async_listener.py)
- [x] RabbitMQ bağlantı ve mesaj alışverişi testleri
- [x] API endpoint test scriptleri çalışır durumda

## Sonraki Adımlar

### Öncelikli:
1. ✅ Eksik API endpoint'lerinin tamamlanması (Tamamlandı)
2. Frontend projesinin oluşturulması ve temel komponentlerin geliştirilmesi
3. ✅ Test script'lerinin geliştirilmesi (Tamamlandı)
4. README ve dokümantasyonun tamamlanması

### İsteğe Bağlı Özellikler (Zaman Kalırsa):
1. ✅ Tahminleme algoritması geliştirme (Basit formda tamamlandı)
2. ✅ WebSocket ile gerçek zamanlı bildirimler (Tamamlandı)
3. Birim testlerin yazılması
4. CI/CD pipeline yapılandırması 