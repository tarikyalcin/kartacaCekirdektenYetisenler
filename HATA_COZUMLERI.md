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

# Hata Çözümleri

Bu dosya, projeyi geliştirirken karşılaşılan önemli hataları ve bunların nasıl çözüldüğünü belgelemektedir.

## 1. Pydantic İmport Hatası

**Hata:**
```
Traceback (most recent call last):
  File "/app/app/config.py", line 2, in <module>
    from pydantic import BaseSettings
ImportError: cannot import name 'BaseSettings' from 'pydantic'
```

**Çözüm:**
Pydantic kütüphanesinin son sürümlerinde (v2.x) `BaseSettings` sınıfı ana paketten çıkarılmış ve `pydantic-settings` paketine taşınmıştır. Problemi çözmek için:

1. `requirements.txt` dosyasına `pydantic-settings` paketi eklendi
2. `config.py` dosyası güncellendi:
```python
from pydantic_settings import BaseSettings
```

## 2. Docker Container Başlatma Sorunu

**Hata:**
Backend servisi sürekli "restarting" durumunda kalıyordu.

**Çözüm:**
Docker compose yapılandırmasında restart politikası güncellendi ve başlatma sırası düzenlendi:
```yaml
restart: on-failure:3  # Sonsuz yeniden başlatma yerine 3 deneme
depends_on:
  - mongodb
  - rabbitmq
```

## 3. RabbitMQ Bağlantı Sorunu

**Hata:**
```
RabbitMQ bağlantısı kurulamadı: [Errno 111] Connect call failed ('172.18.0.2', 5672)
```

**Çözüm:**
1. RabbitMQ servisinin hazır olması için bekleme ve yeniden deneme mekanizması eklendi:
```python
for attempt in range(self.max_retries):
    try:
        # Bağlantı kodları
    except Exception as e:
        logger.warning(f"Bağlantı hatası, yeniden deneniyor: {str(e)}")
        await asyncio.sleep(self.retry_delay)
```

2. Docker compose'da RabbitMQ için sanal host (vhost) ayarları eklendi:
```yaml
environment:
  - RABBITMQ_DEFAULT_VHOST=/
```

## 4. JSON Serileştirme Hatası

**Hata:**
```
TypeError: Object of type datetime is not JSON serializable
```
**ve daha sonra:**
```
TypeError: Object of type ObjectId is not JSON serializable
```

**Çözüm:**
Özel bir JSON Encoder sınıfı oluşturuldu:
```python
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
```

Bu encoder, RabbitMQ mesajlarını göndermeden önce kullanıldı:
```python
json.dumps(message, cls=CustomJSONEncoder)
```

## 5. Worker Başlatma Hatası

**Hata:**
Worker servisi RabbitMQ'ya bağlanamıyordu.

**Çözüm:**
1. Worker'a yeniden deneme mekanizması eklendi:
```python
for attempt in range(self.max_retries):
    try:
        # Worker başlatma kodu
        break  # Başarılı olursa döngüden çık
    except Exception as e:
        logger.error(f"Worker başlatma hatası: {str(e)}")
        await asyncio.sleep(self.retry_delay)
```

2. Ana uygulama başlatma sırasında servisler arasında gecikme eklendi:
```python
# Worker servisinin RabbitMQ'nun hazır olması için biraz bekletme
await asyncio.sleep(2)
await worker.start()
```

## 6. RabbitMQ Yapılandırma Hatası

**Hata:**
```
'Settings' object has no attribute 'RABBITMQ_PASSWORD'
```

**Çözüm:**
RabbitMQ bağlantı URL'si oluşturma kodunu düzelttik ve doğru parametre adlarını kullandık:
```python
# Hatalı
rabbitmq_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}"

# Doğru
rabbitmq_url = settings.RABBITMQ_URL
```

## 7. Hata Yönetimi ve Dayanıklılık

**Sorun:**  
Servisler arasındaki bağımlılıklar ve olası ağ kesintileri sistemin sağlıklı çalışmasını etkileyebilir.

**Çözüm:**
1. Her servis için tekrar deneme mekanizmaları eklendi
2. Her servise bağlantı durumu izleme ve raporlama eklendi
3. Sağlık durumu endpoint'i genişletildi:
```python
@app.get("/health")
async def health_check():
    mongo_status = "healthy" if db.client else "unhealthy"
    rabbitmq_status = "healthy" if rabbitmq.connection else "unhealthy"
    overall_status = "healthy" if mongo_status == "healthy" and rabbitmq_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "mongodb": mongo_status,
            "rabbitmq": rabbitmq_status
        }
    }
``` 