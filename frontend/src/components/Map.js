import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';

const Map = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapInstanceRef.current) {
      // Harita başlatma
      const map = L.map(mapRef.current, {
        center: [41.0082, 28.9784], // İstanbul
        zoom: 4,
        zoomControl: false
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      // Zoom kontrollerini özelleştirme
      L.control.zoom({
        position: 'topleft'
      }).addTo(map);

      // Örnek veri noktaları - gerçek uygulamada API'den çekilecek
      const dummyData = [
        { lat: 41.0082, lng: 28.9784, value: 35, status: 'moderate' }, // İstanbul
        { lat: 39.9334, lng: 32.8597, value: 15, status: 'good' },     // Ankara
        { lat: 38.4237, lng: 27.1428, value: 85, status: 'unhealthy' }, // İzmir
        { lat: 37.0000, lng: 35.3213, value: 120, status: 'danger' }   // Adana
      ];

      // Veri noktalarını ekleme
      dummyData.forEach(point => {
        // Hava kalitesine göre renk belirleme
        let color;
        switch (point.status) {
          case 'good':
            color = '#28a745';
            break;
          case 'moderate':
            color = '#bfd200';
            break;
          case 'unhealthy':
            color = '#ffa500';
            break;
          case 'danger':
            color = '#dc3545';
            break;
          default:
            color = '#28a745';
        }

        // Marker oluşturma
        const marker = L.circleMarker([point.lat, point.lng], {
          radius: 8,
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
              <h3>AQI: ${point.value}</h3>
              <span class="popup-status ${point.status}">${point.status}</span>
            </div>
            <div class="popup-content">
              <p>PM2.5: ${point.value} µg/m³</p>
              <p>Son güncelleme: ${new Date().toLocaleTimeString()}</p>
            </div>
          </div>
        `);
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
  }, []);

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