#!/bin/bash

# Kullanım:
# ./manual-input.sh <latitude> <longitude> <parameter> <value>
# Örnek:
# ./manual-input.sh 41.0082 28.9784 pm25 35.2

# Gerekli parametreleri kontrol et
if [ "$#" -lt 4 ]; then
    echo "Kullanım: $0 <latitude> <longitude> <parameter> <value>"
    echo "Parametreler:"
    echo "  <latitude>   : Enlem (-90 ila 90 arası)"
    echo "  <longitude>  : Boylam (-180 ila 180 arası)"
    echo "  <parameter>  : Kirlilik parametresi (pm25, pm10, no2, so2, o3)"
    echo "  <value>      : Değer (pozitif sayı)"
    exit 1
fi

LATITUDE=$1
LONGITUDE=$2
PARAMETER=$3
VALUE=$4

# İsteğe bağlı ek parametreler
CITY=${5:-""}
COUNTRY=${6:-""}

# API URL'si (geliştirme ortamı için)
API_URL=${API_URL:-"http://localhost:8000/api/data"}

# Parametre doğrulama
if ! [[ $LATITUDE =~ ^-?[0-9]+(\.[0-9]+)?$ ]] || (( $(echo "$LATITUDE < -90 || $LATITUDE > 90" | bc -l) )); then
    echo "Hata: Enlem değeri -90 ile 90 arasında olmalıdır."
    exit 1
fi

if ! [[ $LONGITUDE =~ ^-?[0-9]+(\.[0-9]+)?$ ]] || (( $(echo "$LONGITUDE < -180 || $LONGITUDE > 180" | bc -l) )); then
    echo "Hata: Boylam değeri -180 ile 180 arasında olmalıdır."
    exit 1
fi

if ! [[ "$PARAMETER" =~ ^(pm25|pm10|no2|so2|o3)$ ]]; then
    echo "Hata: Geçersiz parametre. Kabul edilen parametreler: pm25, pm10, no2, so2, o3"
    exit 1
fi

if ! [[ $VALUE =~ ^[0-9]+(\.[0-9]+)?$ ]] || (( $(echo "$VALUE < 0" | bc -l) )); then
    echo "Hata: Değer pozitif bir sayı olmalıdır."
    exit 1
fi

# JSON verisi oluştur
JSON_DATA="{\"latitude\": $LATITUDE, \"longitude\": $LONGITUDE, \"$PARAMETER\": $VALUE"

# İsteğe bağlı alanları ekle
if [ ! -z "$CITY" ]; then
    JSON_DATA="$JSON_DATA, \"city\": \"$CITY\""
fi

if [ ! -z "$COUNTRY" ]; then
    JSON_DATA="$JSON_DATA, \"country\": \"$COUNTRY\""
fi

# JSON'u tamamla
JSON_DATA="$JSON_DATA}"

# API'ye POST isteği gönder
echo "Veri gönderiliyor: $JSON_DATA"
curl -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d "$JSON_DATA" \
     -v 