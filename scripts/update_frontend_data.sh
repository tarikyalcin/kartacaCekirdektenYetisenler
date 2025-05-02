#!/bin/bash

# Script MongoDB'den verileri alıp frontend için JSON dosyalarına kaydeder

# Renk tanımlamaları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Hava Kalitesi Verilerini Güncelleme${NC}"
echo "----------------------------------------"

# MongoDB verilere erişim için Python scriptini çalıştır
echo -e "${GREEN}MongoDB'den verileri alınıyor...${NC}"

# Python environment kontrol et
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Hata: Python bulunamadı. Lütfen Python yükleyin.${NC}"
    exit 1
fi

# Gerekli paketleri kontrol et ve gerekirse kur
$PYTHON_CMD -c "import pymongo" &>/dev/null || {
    echo -e "${YELLOW}PyMongo paketi kuruluyor...${NC}"
    $PYTHON_CMD -m pip install pymongo
}

# MongoDB bağlantı bilgilerini çevre değişkenlerinden al (eğer docker-compose ile çalışıyorsa)
if [ -z "$MONGODB_URL" ]; then
    export MONGODB_URL="mongodb://admin:password@localhost:27017/air_quality_db?authSource=admin"
fi

if [ -z "$MONGODB_DB_NAME" ]; then
    export MONGODB_DB_NAME="air_quality_db"
fi

# Test MongoDB bağlantısını kontrol et
echo "MongoDB bağlantısı test ediliyor..."
$PYTHON_CMD -c "from pymongo import MongoClient; client = MongoClient('$MONGODB_URL'); db = client['$MONGODB_DB_NAME']; print('Bağlantı başarılı!')" || {
    echo -e "${RED}MongoDB bağlantı hatası. Lütfen servisin çalıştığını kontrol edin.${NC}"
    echo "Manuel olarak test veri seti oluşturuluyor..."
}

# Python scriptini çalıştır
echo "Veriler MongoDB'den alınıyor ve JSON dosyalarına kaydediliyor..."
$PYTHON_CMD "$(dirname "$0")/test_mongodb_direct.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Veriler başarıyla güncellendi!${NC}"
    
    # Frontend public/data klasörünün yolunu bul
    FRONTEND_DATA_DIR="$(dirname "$(dirname "$0")")/frontend/public/data"
    
    if [ -d "$FRONTEND_DATA_DIR" ]; then
        echo -e "${GREEN}Şu dosyalar oluşturuldu:${NC}"
        ls -la "$FRONTEND_DATA_DIR"
    fi
else
    echo -e "${RED}Veri güncelleme sırasında bir hata oluştu.${NC}"
fi

echo "----------------------------------------"
echo -e "${YELLOW}İşlem tamamlandı.${NC}" 