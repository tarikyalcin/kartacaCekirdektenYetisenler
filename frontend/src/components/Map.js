import React, { useEffect, useState, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';

const Map = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [airQualityData, setAirQualityData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Hava kalitesi durumuna göre renk belirle
  const getColorByStatus = (status) => {
    switch (status) {
      case 'good':
        return '#28a745'; // Yeşil
      case 'moderate':
        return '#bfd200'; // Sarı-Yeşil
      case 'unhealthy':
        return '#ffa500'; // Turuncu
      case 'very-unhealthy':
        return '#ff4500'; // Kırmızı-Turuncu
      case 'hazardous':
        return '#dc3545'; // Kırmızı
      default:
        return '#28a745';
    }
  };

  // PM2.5 değerine göre durum belirle
  const getStatusByPM25 = (pm25) => {
    if (pm25 <= 15) return 'good';
    if (pm25 <= 50) return 'moderate';
    if (pm25 <= 100) return 'unhealthy';
    if (pm25 <= 150) return 'very-unhealthy';
    return 'hazardous';
  };

  // PM2.5 değerine göre marker boyutu hesapla
  const getMarkerSize = (pm25) => {
    const baseSize = 6;
    const maxSize = 16;
    
    if (pm25 <= 15) return baseSize;
    if (pm25 <= 50) return baseSize + 2;
    if (pm25 <= 100) return baseSize + 4;
    if (pm25 <= 150) return baseSize + 6;
    return maxSize;
  };

  // Verileri yükle
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Hava kalitesi verilerini yükle
        const airQualityResponse = await fetch('/data/air_quality.json');
        const airQualityData = await airQualityResponse.json();
        
        // Anomali verilerini yükle
        const anomalyResponse = await fetch('/data/anomalies.json');
        const anomalyData = await anomalyResponse.json();
        
        setAirQualityData(airQualityData);
        setAnomalyData(anomalyData);
        setLoading(false);
      } catch (error) {
        console.error('Veri yükleme hatası:', error);
        
        // Hata durumunda test verisi oluştur
        const testData = [
          { location: { type: "Point", coordinates: [41.0082, 28.9784] }, pm25: 35, status: 'moderate', city: "İstanbul" },
          { location: { type: "Point", coordinates: [39.9334, 32.8597] }, pm25: 15, status: 'good', city: "Ankara" },
          { location: { type: "Point", coordinates: [38.4237, 27.1428] }, pm25: 85, status: 'unhealthy', city: "İzmir" },
          { location: { type: "Point", coordinates: [37.0000, 35.3213] }, pm25: 120, status: 'very-unhealthy', city: "Adana" }
        ];
        
        setAirQualityData(testData);
        setAnomalyData([]);
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Haritayı oluştur
  useEffect(() => {
    if (!loading && !mapInstanceRef.current) {
      // Harita başlatma
      const map = L.map(mapRef.current, {
        center: [39.0, 35.0], // Türkiye'nin merkezi
        zoom: 6,
        zoomControl: false
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      // Zoom kontrollerini özelleştirme
      L.control.zoom({
        position: 'topleft'
      }).addTo(map);

      // Veri noktalarını ekleme
      airQualityData.forEach(point => {
        // Koordinatları al (farklı formatlara uyum sağla)
        let lat, lng;
        
        if (point.location && point.location.coordinates) {
          // MongoDB GeoJSON formatı
          [lat, lng] = point.location.coordinates;
        } else if (point.lat !== undefined && point.lng !== undefined) {
          // Düz format
          lat = point.lat;
          lng = point.lng;
        } else {
          console.warn('Geçersiz konum formatı:', point);
          return;
        }
        
        // Status değeri varsa kullan, yoksa PM2.5 değerine göre hesapla
        const status = point.status || getStatusByPM25(point.pm25);
        const color = getColorByStatus(status);
        const radius = getMarkerSize(point.pm25);
        
        // Marker oluşturma
        const marker = L.circleMarker([lat, lng], {
          radius: radius,
          fillColor: color,
          color: '#fff',
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        }).addTo(map);

        // Popup oluşturma
        marker.bindPopup(`
          <div class="map-popup">
            <div class="popup-header">
              <h3>${point.city || 'Bilinmeyen Konum'}</h3>
              <span class="popup-status ${status}">${status}</span>
            </div>
            <div class="popup-content">
              <p>PM2.5: ${point.pm25} µg/m³</p>
              <p>PM10: ${point.pm10 || 'N/A'} µg/m³</p>
              <p>NO2: ${point.no2 || 'N/A'} µg/m³</p>
              <p>SO2: ${point.so2 || 'N/A'} µg/m³</p>
              <p>O3: ${point.o3 || 'N/A'} µg/m³</p>
              <p>Son güncelleme: ${new Date(point.timestamp || Date.now()).toLocaleString('tr-TR')}</p>
            </div>
          </div>
        `);
      });

      // Anomali noktalarını işaretle
      anomalyData.forEach(anomaly => {
        if (anomaly.location && anomaly.location.coordinates) {
          const [lat, lng] = anomaly.location.coordinates;
          
          // Pulsating circle for anomalies
          const pulsingIcon = L.divIcon({
            className: 'pulsing-icon',
            html: `<div class="pulse-icon ${anomaly.type}"></div>`,
            iconSize: [20, 20]
          });
          
          const marker = L.marker([lat, lng], {
            icon: pulsingIcon
          }).addTo(map);
          
          // Anomali popup içeriği
          marker.bindPopup(`
            <div class="map-popup anomaly">
              <div class="popup-header">
                <h3>${anomaly.city || 'Bilinmeyen Konum'}</h3>
                <span class="popup-status alert">Anomali!</span>
              </div>
              <div class="popup-content">
                <p><strong>Tür:</strong> ${anomaly.type}</p>
                <p><strong>Parametre:</strong> ${anomaly.parameter}</p>
                <p><strong>Değer:</strong> ${anomaly.value} µg/m³</p>
                ${anomaly.threshold ? `<p><strong>Eşik Değeri:</strong> ${anomaly.threshold} µg/m³</p>` : ''}
                ${anomaly.previous_value ? `<p><strong>Önceki Değer:</strong> ${anomaly.previous_value} µg/m³</p>` : ''}
                <p><strong>Tespit Zamanı:</strong> ${new Date(anomaly.detected_at).toLocaleString('tr-TR')}</p>
              </div>
            </div>
          `);
        }
      });

      mapInstanceRef.current = map;
    }

    // Temizleme
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [loading, airQualityData, anomalyData]);

  return (
    <div className="map-container">
      <div ref={mapRef} className="map"></div>
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-color good"></span>
          <span className="legend-label">İyi</span>
        </div>
        <div className="legend-item">
          <span className="legend-color moderate"></span>
          <span className="legend-label">Orta</span>
        </div>
        <div className="legend-item">
          <span className="legend-color unhealthy"></span>
          <span className="legend-label">Sağlıksız</span>
        </div>
        <div className="legend-item">
          <span className="legend-color very-unhealthy"></span>
          <span className="legend-label">Çok Sağlıksız</span>
        </div>
        <div className="legend-item">
          <span className="legend-color hazardous"></span>
          <span className="legend-label">Tehlikeli</span>
        </div>
      </div>
    </div>
  );
};

export default Map; 