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
  
  const [anomalies, setAnomalies] = useState([]);
  const [isLiveMonitoringActive, setIsLiveMonitoringActive] = useState(true);

  // İstatistik verilerini ve anomalileri yükle
  useEffect(() => {
    const fetchData = async () => {
      try {
        // İstatistik verilerini yükle
        const statsResponse = await fetch('/data/stats.json');
        const statsData = await statsResponse.json();
        
        // Anomali verilerini yükle
        const anomalyResponse = await fetch('/data/anomalies.json');
        const anomalyData = await anomalyResponse.json();
        
        setStats(statsData);
        setAnomalies(anomalyData);
      } catch (error) {
        console.error('Veri yükleme hatası:', error);
        // Hata durumunda varsayılan değerleri kullan
      }
    };
    
    fetchData();
    
    // Canlı güncellemeler için düzenli olarak verileri yenile
    if (isLiveMonitoringActive) {
      const intervalId = setInterval(() => {
        fetchData();
      }, 30000); // 30 saniyede bir güncelle
      
      return () => clearInterval(intervalId);
    }
  }, [isLiveMonitoringActive]);
  
  // Canlı izleme durumunu değiştir
  const toggleLiveMonitoring = () => {
    setIsLiveMonitoringActive(!isLiveMonitoringActive);
  };

  return (
    <div className="app">
      <Header />
      <main className="content">
        <h1>Hava Kalitesi İzleme Platformu</h1>
        <p className="subtitle">Dünya genelinde hava kirliliği verilerini gerçek zamanlı olarak izleyin</p>
        
        <div className="live-status">
          <button 
            className="live-toggle-btn" 
            onClick={toggleLiveMonitoring}
          >
            <span className={`status-indicator ${isLiveMonitoringActive ? 'active' : ''}`}></span>
            <span className="status-text">Canlı İzleme {isLiveMonitoringActive ? 'Aktif' : 'Pasif'}</span>
          </button>
        </div>
        
        <Dashboard stats={stats} />
        
        <div className="main-content">
          <div className="map-section">
            <h2>Gerçek Zamanlı Hava Kalitesi Haritası</h2>
            <Map />
          </div>
          
          <div className="side-panel">
            <AnomalyAlerts anomalies={anomalies} />
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