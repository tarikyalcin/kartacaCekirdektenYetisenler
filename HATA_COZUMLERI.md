# 🐛 Karşılaşılan Hatalar ve Çözümleri

## RabbitMQ Bağlantı Hataları

### 1. "Not_Authorized" Hatası
**Hata:** RabbitMQ yönetim paneline giriş yaparken "Not_Authorized" hatası aldım.
**Çözüm:** 
- Docker containerını yeniden başlattım
- Portları değiştirdim (5672 -> 5673 ve 15672 -> 15673)
- Yeni portlarla tekrar denediğimde sorun çözüldü

### 2. "Port is already allocated" Hatası
**Hata:** Docker containerı başlatırken "port is already allocated" hatası aldım.
**Çözüm:**
- `docker-compose.yml` dosyasında portları değiştirdim:
  - 5672 -> 5673 (AMQP)
  - 15672 -> 15673 (Yönetim)
- Bu değişiklik sonrası container başarıyla başladı

## Docker Sorunları

### 1. Docker Desktop Bağlantı Hatası
**Hata:** Docker komutlarını çalıştırırken "cannot connect to Docker daemon" benzeri bir hata aldım.
**Çözüm:**
- Docker Desktop'ın çalışır durumda olduğundan emin oldum
- Docker Desktop'ı yeniden başlattım
- Komutları tekrar çalıştırdığımda sorun çözüldü

## Öğrenilen Dersler
1. Port çakışmaları olduğunda alternatif portlar kullanmak iyi bir çözüm
2. Docker containerlarını yönetirken önce mevcut durumu kontrol etmek önemli
3. Hata mesajlarını dikkatlice okuyup, adım adım çözüm denemek gerekiyor
4. Yapılan değişiklikleri not almak, benzer sorunlarla karşılaşıldığında yardımcı oluyor 