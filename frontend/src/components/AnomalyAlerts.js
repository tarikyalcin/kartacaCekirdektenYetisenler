import React from 'react';
import './AnomalyAlerts.css';

const AnomalyAlerts = ({ anomalies = [] }) => {
  // Anomali türüne göre metin açıklaması oluştur
  const getAnomalyTypeText = (type) => {
    switch (type) {
      case 'threshold_exceeded':
        return 'Eşik Değeri Aşıldı';
      case 'sudden_increase':
        return 'Ani Artış Tespit Edildi';
      case 'who_limit_exceeded':
        return 'WHO Limiti Aşıldı';
      default:
        return 'Anomali';
    }
  };

  // Anomali türüne göre sınıf adı belirle
  const getAnomalyTypeClass = (type) => {
    switch (type) {
      case 'threshold_exceeded':
        return 'threshold';
      case 'sudden_increase':
        return 'sudden';
      case 'who_limit_exceeded':
        return 'who';
      default:
        return '';
    }
  };

  // Tarih formatını düzenle
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('tr-TR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateString || '';
    }
  };

  return (
    <div className="anomaly-alerts">
      <h2>Anomali Uyarıları</h2>
      <div className="alerts-container">
        {anomalies.length === 0 ? (
          <div className="no-alerts">
            <div className="no-alerts-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="m15 9-6 6"></path>
                <path d="m9 9 6 6"></path>
              </svg>
            </div>
            <p>Şu anda aktif anomali uyarısı bulunmuyor</p>
          </div>
        ) : (
          <>
            {anomalies.map((alert, index) => (
              <div key={alert._id || index} className={`alert-item ${getAnomalyTypeClass(alert.type)}`}>
                <div className="alert-header">
                  <div className="alert-type">{getAnomalyTypeText(alert.type)}</div>
                  <div className="alert-time">{formatDate(alert.detected_at)}</div>
                </div>
                <div className="alert-location">{alert.city || 'Bilinmeyen Konum'}</div>
                <div className="alert-details">
                  <div className="alert-value">
                    <span className="detail-label">Değer:</span>
                    <span className="detail-value">{alert.value} µg/m³</span>
                  </div>
                  {alert.threshold && (
                    <div className="alert-threshold">
                      <span className="detail-label">Eşik:</span>
                      <span className="detail-value">{alert.threshold} µg/m³</span>
                    </div>
                  )}
                  {alert.previous_value && (
                    <div className="alert-previous">
                      <span className="detail-label">Önceki:</span>
                      <span className="detail-value">{alert.previous_value} µg/m³</span>
                    </div>
                  )}
                  <div className="alert-parameter">
                    <span className="detail-label">Parametre:</span>
                    <span className="detail-value">{alert.parameter}</span>
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default AnomalyAlerts; 