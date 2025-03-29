#!/bin/bash

# Kullanım:
# ./auto-test.sh [options]
# Opsiyonlar:
#   --duration=<seconds>: Script'in çalışma süresi (saniye), varsayılan: 60
#   --rate=<requests_per_second>: Saniyede gönderilecek istek sayısı, varsayılan: 1
#   --anomaly-chance=<percentage>: Anomali oluşturma olasılığı (0-100), varsayılan: 10

# Varsayılan değerler
DURATION=60
RATE=1
ANOMALY_CHANCE=10
API_URL=${API_URL:-"http://localhost:8000/api/data"}

# Komut satırı parametrelerini işle
for i in "$@"; do
    case $i in
        --duration=*)
            DURATION="${i#*=}"
            shift
            ;;
        --rate=*)
            RATE="${i#*=}"
            shift
            ;;
        --anomaly-chance=*)
            ANOMALY_CHANCE="${i#*=}"
            shift
            ;;
        *)
            echo "Bilinmeyen parametre: $i"
            echo "Kullanım: $0 [options]"
            echo "Opsiyonlar:"
            echo "  --duration=<seconds>: Script'in çalışma süresi (saniye), varsayılan: 60"
            echo "  --rate=<requests_per_second>: Saniyede gönderilecek istek sayısı, varsayılan: 1"
            echo "  --anomaly-chance=<percentage>: Anomali oluşturma olasılığı (0-100), varsayılan: 10"
            exit 1
            ;;
    esac
done

echo "Test Ayarları:"
echo "  Süre: $DURATION saniye"
echo "  Hız: $RATE istek/saniye"
echo "  Anomali Olasılığı: $ANOMALY_CHANCE%"
echo "  API URL: $API_URL"

# WHO standartlarına göre normal değer aralıkları
# PM2.5: 0-25 μg/m³
# PM10: 0-50 μg/m³
# NO2: 0-200 μg/m³
# SO2: 0-500 μg/m³
# O3: 0-100 μg/m³

# Parametreler ve değer aralıkları
declare -A PARAMETERS
PARAMETERS=(
    ["pm25"]="0,25"
    ["pm10"]="0,50"
    ["no2"]="0,200"
    ["so2"]="0,500"
    ["o3"]="0,100"
)

# Anomali için çarpan değerleri
declare -A ANOMALY_MULTIPLIERS
ANOMALY_MULTIPLIERS=(
    ["pm25"]="2,5"
    ["pm10"]="2,4"
    ["no2"]="1.5,3"
    ["so2"]="1.5,2.5"
    ["o3"]="2,4"
)

# Dünyadaki belli başlı şehirler ve koordinatları (örnek)
declare -A CITIES
CITIES=(
    ["Istanbul"]="41.0082,28.9784,Turkey"
    ["Ankara"]="39.9334,32.8597,Turkey"
    ["Izmir"]="38.4237,27.1428,Turkey"
    ["New York"]="40.7128,-74.0060,USA"
    ["London"]="51.5074,-0.1278,UK"
    ["Paris"]="48.8566,2.3522,France"
    ["Tokyo"]="35.6762,139.6503,Japan"
    ["Beijing"]="39.9042,116.4074,China"
    ["Delhi"]="28.7041,77.1025,India"
    ["Sydney"]="-33.8688,151.2093,Australia"
)

# Başlangıç zamanı
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))
REQUEST_INTERVAL=$(awk "BEGIN {print 1 / $RATE}")

# İstek sayacı
REQUEST_COUNT=0

while [ $(date +%s) -lt $END_TIME ]; do
    # Rastgele bir şehir seç
    CITY_INDEX=$((RANDOM % ${#CITIES[@]}))
    CITY_NAME=$(echo ${!CITIES[@]} | cut -d' ' -f$((CITY_INDEX + 1)))
    CITY_INFO="${CITIES[$CITY_NAME]}"
    
    LAT=$(echo $CITY_INFO | cut -d',' -f1)
    LON=$(echo $CITY_INFO | cut -d',' -f2)
    COUNTRY=$(echo $CITY_INFO | cut -d',' -f3)
    
    # Rastgele bir parametre seç
    PARAM_INDEX=$((RANDOM % ${#PARAMETERS[@]}))
    PARAM_NAME=$(echo ${!PARAMETERS[@]} | cut -d' ' -f$((PARAM_INDEX + 1)))
    
    # Parametre değer aralığı
    PARAM_RANGE="${PARAMETERS[$PARAM_NAME]}"
    MIN_VALUE=$(echo $PARAM_RANGE | cut -d',' -f1)
    MAX_VALUE=$(echo $PARAM_RANGE | cut -d',' -f2)
    
    # Anomali kontrolü
    IS_ANOMALY=0
    if [ $((RANDOM % 100)) -lt $ANOMALY_CHANCE ]; then
        IS_ANOMALY=1
        
        # Anomali çarpanı
        ANOMALY_RANGE="${ANOMALY_MULTIPLIERS[$PARAM_NAME]}"
        MIN_MULT=$(echo $ANOMALY_RANGE | cut -d',' -f1)
        MAX_MULT=$(echo $ANOMALY_RANGE | cut -d',' -f2)
        
        # Rastgele anomali çarpanı (MIN_MULT ile MAX_MULT arasında)
        MULTIPLIER=$(awk "BEGIN {srand(); print $MIN_MULT + rand() * ($MAX_MULT - $MIN_MULT)}")
        
        # Anomali değeri hesapla
        VALUE=$(awk "BEGIN {srand(); print ($MIN_VALUE + rand() * ($MAX_VALUE - $MIN_VALUE)) * $MULTIPLIER}")
    else
        # Normal değer (MIN_VALUE ile MAX_VALUE arasında)
        VALUE=$(awk "BEGIN {srand(); print $MIN_VALUE + rand() * ($MAX_VALUE - $MIN_VALUE)}")
    fi
    
    # Değeri 2 ondalık basamağa yuvarla
    VALUE=$(printf "%.2f" $VALUE)
    
    # JSON verisi oluştur
    JSON_DATA="{\"latitude\": $LAT, \"longitude\": $LON, \"$PARAM_NAME\": $VALUE, \"city\": \"$CITY_NAME\", \"country\": \"$COUNTRY\"}"
    
    # API'ye POST isteği gönder
    if [ $IS_ANOMALY -eq 1 ]; then
        echo "[$REQUEST_COUNT] ANOMALİ veri gönderiliyor: $JSON_DATA"
    else
        echo "[$REQUEST_COUNT] Normal veri gönderiliyor: $JSON_DATA"
    fi
    
    curl -s -X POST "$API_URL" \
         -H "Content-Type: application/json" \
         -d "$JSON_DATA" > /dev/null
    
    # İstek sayacını artır
    REQUEST_COUNT=$((REQUEST_COUNT + 1))
    
    # İstek aralığı kadar bekle
    sleep $REQUEST_INTERVAL
done

echo "Test tamamlandı. Toplam $REQUEST_COUNT istek gönderildi." 