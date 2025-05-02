# Hava Kirliliği İzleme Platformu: Kurulum ve Çalıştırma Rehberi

Bu döküman, hava kirliliği izleme platformunun kurulumu ve çalıştırılması için gerekli adımları içermektedir.

## Gereksinimler

- Node.js (v14 veya üzeri)
- Python (v3.6 veya üzeri)
- MongoDB
- Git

## Adım Adım Kurulum ve Çalıştırma

### 1. Projeyi İndirme

```bash
git clone https://github.com/[kullanici-adi]/kartacaCekirdektenYetisenler.git
cd kartacaCekirdektenYetisenler
```

### 2. Backend Kurulumu

Backend için gerekli Python bağımlılıklarını yükleyin:

```bash
cd backend
pip install -r requirements.txt
```

### 3. MongoDB Kurulumu ve Veri Yükleme

MongoDB'nin kurulu ve çalışıyor olduğundan emin olun.

Örnek verileri MongoDB'ye eklemek için:

```bash
python scripts/add_real_city_data.py
```

Bu script Ankara, İstanbul, Niğde, Yalova, Kütahya, Erzurum, Rize, Mardin ve Kocaeli şehirleri için gerçekçi hava kalitesi verilerini ve anomali kayıtlarını veritabanına ekleyecektir.

### 4. Frontend Kurulumu ve Çalıştırılması

Frontend uygulamasını kurmak ve çalıştırmak için:

```bash
cd frontend
npm install
```

Kurulum tamamlandıktan sonra, uygulamayı başlatmak için:

Windows PowerShell üzerinde:
```powershell
$env:PORT = "3005"; npm start
```

Bash/Linux/Mac üzerinde:
```bash
PORT=3005 npm start
```

Uygulama başarıyla başlatıldığında, tarayıcınızda otomatik olarak açılacaktır veya şu adresten erişebilirsiniz:
```
http://localhost:3005
```

### 5. Backend Servislerini Çalıştırma

Backend servislerini çalıştırmak için yeni bir terminal açın:

```bash
cd backend
python app.py
```

### 6. Docker ile Çalıştırma (Opsiyonel)

Tüm sistemi Docker ile çalıştırmak isterseniz:

```bash
docker-compose up
```

## Harita Görüntüleme Özellikleri

Harita görüntülemede şu özellikler bulunmaktadır:

- PM2.5 değerine göre dinamik marker boyutları
- 5 farklı seviyede renk kodlaması (iyi, orta, sağlıksız, çok sağlıksız, tehlikeli)
- Anomali noktaları için özel işaretçiler
- Türkiye merkezli görünüm
- Sadece belirlenen şehirlerin (Ankara, İstanbul, Niğde, Yalova, Kütahya, Erzurum, Rize, Mardin ve Kocaeli) gösterimi

## Sorun Giderme

### Port Çakışması
Eğer 3005 portu başka bir uygulama tarafından kullanılıyorsa, farklı bir port numarası kullanabilirsiniz:

```powershell
$env:PORT = "3006"; npm start
```

### MongoDB Bağlantı Hatası
MongoDB bağlantı hatası alırsanız, MongoDB servisinin çalıştığından emin olun ve bağlantı bilgilerini kontrol edin.

### PowerShell Komut Sorunları
PowerShell'de && operatörü çalışmadığı için, komutları ayrı ayrı çalıştırın veya noktalı virgül kullanın:

```powershell
cd frontend; npm start
```

## İletişim ve Destek

Herhangi bir sorun yaşarsanız veya desteğe ihtiyacınız olursa, lütfen proje yöneticisi ile iletişime geçin. 