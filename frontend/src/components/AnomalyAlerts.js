import React, { useState, useEffect } from 'react';
import './AnomalyAlerts.css';

const AnomalyAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [isLive, setIsLive] = useState(true);

  // Burada normalde WebSocket veya SSE bağlantısı ile
  // backend'den anomali verileri alınacak
  useEffect(() => {
    // Örnek veri oluşturma
    const exampleAlerts = [];
    
    // Şu anda örnek veri göstermiyoruz
    setAlerts(exampleAlerts);
    
    // Gerçek bir WebSocket bağlantısı şöyle olabilir:
    // const socket = new WebSocket('ws://localhost:8000/ws/anomalies');
    // socket.onmessage = (event) => {
    //   const data = JSON.parse(event.data);
    //   setAlerts(prev => [data, ...prev].slice(0, 10));
    // };
    // 
    // return () => {
    //   socket.close();
    // };
  }, []);

  return (
    <div className="anomaly-alerts">
      <div className="alerts-header">
        <h2>Anomali Uyarıları</h2>
        <div className="live-indicator">
          <span className={`indicator-dot ${isLive ? 'active' : ''}`}></span>
          <span>Canlı</span>
        </div>
      </div>
      
      {alerts.length > 0 ? (
        <div className="alerts-list">
          {alerts.map((alert, index) => (
            <div key={index} className="alert-item">
              <div className="alert-header">
                <span className={`alert-type ${alert.severity}`}>{alert.type}</span>
                <span className="alert-time">{alert.time}</span>
              </div>
              <div className="alert-location">{alert.location}</div>
              <div className="alert-message">{alert.message}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-alerts">
          <div className="no-alerts-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 8v4"></path>
              <path d="M12 16h.01"></path>
            </svg>
          </div>
          <p>Şu anda aktif uyarı bulunmuyor. Sistemde anomali tespit edildiğinde burada görüntülenecektir.</p>
        </div>
      )}
    </div>
  );
};

export default AnomalyAlerts; 