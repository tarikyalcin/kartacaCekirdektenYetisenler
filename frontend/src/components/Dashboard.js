import React from 'react';
import './Dashboard.css';

const Dashboard = ({ stats }) => {
  return (
    <div className="dashboard">
      <div className="stat-card">
        <div className="stat-icon alert">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
            <path d="M12 9v4"></path>
            <path d="M12 17h.01"></path>
          </svg>
        </div>
        <div className="stat-details">
          <h3 className="stat-value">{stats.totalAlerts}</h3>
          <p className="stat-label">Toplam Uyarı</p>
          <p className="stat-period">Son 24 Saat</p>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon warning">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"></path>
          </svg>
        </div>
        <div className="stat-details">
          <h3 className="stat-value">{stats.whoLimitExceeded}</h3>
          <p className="stat-label">WHO Limiti Aşan</p>
          <p className="stat-period">Son 24 Saat</p>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon increase">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 7 8 7"></path>
            <path d="M19 4 22 7 19 10"></path>
            <path d="M3 17H16"></path>
            <path d="M6 20 3 17 6 14"></path>
          </svg>
        </div>
        <div className="stat-details">
          <h3 className="stat-value">{stats.suddenIncreases}</h3>
          <p className="stat-label">Ani Artışlar</p>
          <p className="stat-period">Son 24 Saat</p>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon region">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="m7.21 15 2.72-4.68c.5-.87 1.71-.38 1.71.48v5.8c0 .83 1.21 1.28 1.71.48l2.72-4.68"></path>
          </svg>
        </div>
        <div className="stat-details">
          <h3 className="stat-value">{stats.affectedRegions}</h3>
          <p className="stat-label">Etkilenen Bölgeler</p>
          <p className="stat-period">Benzersiz Konum</p>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon high-value">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 20h.01"></path>
            <path d="M7 20v-4"></path>
            <path d="M12 20v-8"></path>
            <path d="M17 20V8"></path>
            <path d="M22 4v16"></path>
          </svg>
        </div>
        <div className="stat-details">
          <h3 className="stat-value">{stats.highestValue}</h3>
          <p className="stat-label">En Yüksek Değer</p>
          <p className="stat-period">- (µg/m³)</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 