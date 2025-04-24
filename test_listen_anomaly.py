import pika
import json
import time

# RabbitMQ bağlantısı
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5673,  # Docker compose'daki port yönlendirmesine göre ayarlanmıştır
        virtual_host='/',
        credentials=pika.PlainCredentials('admin', 'password')
    )
)

channel = connection.channel()

# Kuyruk tanımla
queue_name = "anomaly_notifications"

# Mesaj callback fonksiyonu
def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"\n[*] Anomali mesajı alındı:")
        print(f"    - Tip: {message.get('type')}")
        if 'data' in message:
            data = message['data']
            print(f"    - Parametre: {data.get('parameter')}")
            print(f"    - Konum: {data.get('location')}")
            print(f"    - Değer: {data.get('actual_value')}")
            print(f"    - Şiddet: {data.get('severity')}")
            print(f"    - Zaman: {data.get('detected_at')}")
    except json.JSONDecodeError:
        print(f"[!] JSON çözümlenemedi: {body}")
    except Exception as e:
        print(f"[!] Hata: {str(e)}")
    
    # Mesajı işaretleme (acknowledgment)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Kuyruktan mesaj almak için tüketici başlat
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback
)

print(f"[*] '{queue_name}' kuyruğu dinleniyor. Çıkmak için CTRL+C tuşlarına basın.")

try:
    # Tüketmeye başla
    channel.start_consuming()
except KeyboardInterrupt:
    # Kullanıcı CTRL+C ile durdurduğunda
    channel.stop_consuming()

# Bağlantıyı kapat
connection.close() 