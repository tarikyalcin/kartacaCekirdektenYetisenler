# Gerçek Zamanlı Hava Kirliliği İzleme Platformu - Yol Haritası

## Teknoloji Seçimleri

- **Backend:** Python (FastAPI) - Hızlı geliştirme, kolay öğrenme eğrisi ve güçlü performans
- **Mimari:** Monolitik (başlangıç için daha basit, daha az karmaşıklık)
- **Veritabanı:** MongoDB (esnek şema, zaman serisi koleksiyonları için destek)
- **Kuyruklama Sistemi:** RabbitMQ (kurulumu ve kullanımı daha kolay)
- **Frontend:** React (geniş ekosistem ve hazır komponentler)
- **Harita Kütüphanesi:** Leaflet (açık kaynak ve kullanımı kolay)
- **Grafik Kütüphanesi:** Chart.js (basit ve kullanımı kolay)

## Detaylı Yol Haritası

### 1. Proje Yapısının Oluşturulması (2-3 gün)

#### Backend (FastAPI):
- [x] Proje dizin yapısının oluşturulması
- [x] Gerekli kütüphanelerin kurulumu (FastAPI, pika, pymongo, pandas)
- [x] Temel API yapısının kurulması
- [x] Veritabanı ve kuyruklama bağlantılarının yapılandırılması

#### Frontend (React):
- [x] Create React App ile proje oluşturma
- [x] Gerekli kütüphanelerin kurulumu (leaflet, chart.js, axios, socket.io-client)
- [x] Temel sayfa yapısının ve komponentlerin planlanması

#### Docker:
- [x] Backend için Dockerfile oluşturma
- [x] Frontend için Dockerfile oluşturma
- [x] Docker-compose.yml oluşturma (MongoDB, RabbitMQ, Backend, Frontend)

### 2. Veritabanı ve Kuyruklama Sisteminin Kurulması (2 gün)

#### MongoDB:
- [x] Veritabanı ve koleksiyon yapısının tasarımı
- [x] Zaman serisi koleksiyonlarının oluşturulması
- [x] İndeksleme stratejisinin belirlenmesi
- [x] Coğrafi sorgular için indekslerin yapılandırılması

#### RabbitMQ:
- [x] Kuyruk yapılandırması
- [x] Exchange ve binding tanımları
- [x] Mesaj formatı belirleme

### 3. Backend Geliştirme (5-7 gün)

#### API Endpoints:
- [ ] Veri alma endpoint'i (`/api/data`)
- [ ] Belirli bir konum için hava kalitesi verileri getiren endpoint (`/api/air-quality/{location}`)
- [ ] Belirli bir zaman aralığında tespit edilen anomalileri listeleyen endpoint (`/api/anomalies`)
- [ ] Coğrafi bölgeye göre kirlilik yoğunluğunu getiren endpoint (`/api/pollution-density`)

#### Veri İşleme:
- [ ] RabbitMQ'dan mesajları alma ve işleme
- [ ] Anomali tespiti algoritmaları (Z-score, WHO threshold değerleri)
- [ ] İşlenmiş verileri MongoDB'ye kaydetme
- [ ] WebSocket veya SSE ile gerçek zamanlı uyarılar gönderme

### 4. Frontend Geliştirme (5-7 gün)

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

### 5. Test Scriptleri Geliştirme (2-3 gün)

#### Manuel Veri Girişi Script'i:
- [x] Bash script oluşturma (`manual-input.sh`)
- [x] API ile iletişim kurma
- [x] Parametreleri doğrulama ve işleme

#### Otomatik Test Script'i:
- [x] Bash script oluşturma (`auto-test.sh`)
- [x] Rastgele konum ve kirlilik değerleri oluşturma
- [x] Anomali senaryoları oluşturma
- [x] İstek oranı ve çalışma süresi kontrolleri

### 6. Sistemin Entegrasyonu ve Testleri (3-4 gün)

- [ ] Backend ve frontend entegrasyonu
- [ ] Sistemin uçtan uca testleri
- [ ] Anomali tespiti testleri
- [ ] Performans testleri
- [ ] Hata ayıklama

### 7. Containerization ve Dağıtım (2-3 gün)

- [x] Dockerfile'ların optimize edilmesi
- [x] Docker-compose yapılandırmasının tamamlanması
- [ ] Ortam değişkenlerinin yapılandırılması
- [ ] Dağıtım testleri
- [ ] Yük testleri

### 8. Dokümantasyon (2-3 gün)

- [ ] README dosyasının hazırlanması
- [ ] API dokümantasyonu (Swagger/OpenAPI)
- [ ] Kurulum ve kullanım rehberi
- [ ] Sorun giderme rehberi
- [ ] Proje mimarisi ve teknoloji seçimleri açıklaması

## Sistem Mimarisi ve Veri Akışı

### Veri Girişi:
- Test scriptleri (manual-input.sh veya auto-test.sh) HTTP isteği ile veriyi backend'e gönderir.

### Veri İşleme:
- Backend alınan veriyi RabbitMQ'ya gönderir.
- Worker RabbitMQ'dan veriyi alır, işler ve anomali tespiti yapar.
- İşlenen veri MongoDB'ye kaydedilir.
- Anomali tespit edilirse, WebSocket/SSE üzerinden frontend'e bildirim gönderilir.

### Veri Sorgulama:
- Frontend, kullanıcı isteklerine göre API endpoint'lerini çağırır.
- Backend, MongoDB'den verileri sorgular ve frontend'e döner.
- Frontend, verileri harita ve grafikler üzerinde görselleştirir. 