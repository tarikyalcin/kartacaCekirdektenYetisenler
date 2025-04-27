import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Map from './components/Map';
import AnomalyAlerts from './components/AnomalyAlerts';
import TrendChart from './components/TrendChart';

function App() {
  const [stats, setStats] = useState({
    totalAlerts: 0,
    whoLimitExceeded: 0,
    suddenIncreases: 0,
    affectedRegions: 0,
    highestValue: '-'
  });
  
  const [isLiveMonitoringActive, setIsLiveMonitoringActive] = useState(true);

  // Burada backend API'sinden verileri çekebilirsiniz
  useEffect(() => {
    // Örnek veri çekme işlemi
    // fetch('/api/dashboard-stats').then(...)
    
    // Şimdilik örnek veri kullanıyoruz
    setStats({
      totalAlerts: 0,
      whoLimitExceeded: 0,
      suddenIncreases: 0,
      affectedRegions: 0,
      highestValue: '-'
    });
  }, []);

  return (
    <div className="app">
      <Header />
      <main className="content">
        <h1>Hava Kalitesi İzleme Platformu</h1>
        <p className="subtitle">Dünya genelinde hava kirliliği verilerini gerçek zamanlı olarak izleyin</p>
        
        <div className="live-status">
          <span className={`status-indicator ${isLiveMonitoringActive ? 'active' : ''}`}></span>
          <span className="status-text">Canlı İzleme {isLiveMonitoringActive ? 'Aktif' : 'Pasif'}</span>
        </div>
        
        <Dashboard stats={stats} />
        
        <div className="main-content">
          <div className="map-section">
            <h2>Gerçek Zamanlı Hava Kalitesi Haritası</h2>
            <Map />
          </div>
          
          <div className="side-panel">
            <AnomalyAlerts />
          </div>
        </div>
        
        <TrendChart />
        
      </main>
      <footer className="footer">
        <p>&copy; 2025 Hava Kalitesi İzleme Platformu. Tüm hakları saklıdır.</p>
        <div className="footer-links">
          <a href="#">Gizlilik Politikası</a>
          <a href="#">Hakkımızda</a>
          <a href="#">İletişim</a>
        </div>
      </footer>
    </div>
  );
}

export default App; 