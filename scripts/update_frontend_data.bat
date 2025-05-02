@echo off
:: Script MongoDB'den verileri alıp frontend için JSON dosyalarına kaydeder

echo Hava Kalitesi Verilerini Güncelleme
echo ----------------------------------------

:: MongoDB verilere erişim için Python scriptini çalıştır
echo MongoDB'den verileri alınıyor...

:: Python environment kontrol et
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Hata: Python bulunamadı. Lütfen Python yükleyin.
    exit /b 1
)

:: Gerekli paketleri kontrol et ve gerekirse kur
python -c "import pymongo" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo PyMongo paketi kuruluyor...
    python -m pip install pymongo
)

:: MongoDB bağlantı bilgilerini çevre değişkenlerinden al (eğer docker-compose ile çalışıyorsa)
if "%MONGODB_URL%"=="" (
    set MONGODB_URL=mongodb://admin:password@localhost:27017/air_quality_db?authSource=admin
)

if "%MONGODB_DB_NAME%"=="" (
    set MONGODB_DB_NAME=air_quality_db
)

:: Test MongoDB bağlantısını kontrol et
echo MongoDB bağlantısı test ediliyor...
python -c "from pymongo import MongoClient; client = MongoClient('%MONGODB_URL%'); db = client['%MONGODB_DB_NAME%']; print('Bağlantı başarılı!')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo MongoDB bağlantı hatası. Lütfen servisin çalıştığını kontrol edin.
    echo Manuel olarak test veri seti oluşturuluyor...
)

:: Python scriptini çalıştır
echo Veriler MongoDB'den alınıyor ve JSON dosyalarına kaydediliyor...
python "%~dp0test_mongodb_direct.py"

if %ERRORLEVEL% equ 0 (
    echo Veriler başarıyla güncellendi!
    
    :: Frontend public/data klasörünün yolunu bul
    set FRONTEND_DATA_DIR="%~dp0..\frontend\public\data"
    
    if exist %FRONTEND_DATA_DIR% (
        echo Şu dosyalar oluşturuldu:
        dir %FRONTEND_DATA_DIR%
    )
) else (
    echo Veri güncelleme sırasında bir hata oluştu.
)

echo ----------------------------------------
echo İşlem tamamlandı.
pause 