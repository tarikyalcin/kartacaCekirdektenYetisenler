import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './TrendChart.css';

// Chart.js'yi kaydedin
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TrendChart = () => {
  const [activeParameter, setActiveParameter] = useState('pm25');
  const [activeTimeframe, setActiveTimeframe] = useState('24h');
  
  // Veri yoksa gösterilecek mesaj
  const [hasData, setHasData] = useState(false);

  // Chart.js için veri yapılandırması
  const chartData = {
    labels: [], // Boş etiketler (veri yok)
    datasets: [
      {
        label: 'PM2.5',
        data: [], // Boş veri (veri yok)
        fill: false,
        backgroundColor: 'rgba(103, 80, 229, 0.2)',
        borderColor: 'rgba(103, 80, 229, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(103, 80, 229, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(103, 80, 229, 1)',
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const handleParameterChange = (param) => {
    setActiveParameter(param);
  };

  const handleTimeframeChange = (timeframe) => {
    setActiveTimeframe(timeframe);
  };

  return (
    <div className="trend-chart-container">
      <h2>Hava Kalitesi Trendi</h2>
      
      <div className="chart-controls">
        <div className="parameter-controls">
          <button 
            className={`control-btn ${activeParameter === 'pm25' ? 'active' : ''}`}
            onClick={() => handleParameterChange('pm25')}
          >
            PM2.5
          </button>
          <button 
            className={`control-btn ${activeParameter === 'pm10' ? 'active' : ''}`}
            onClick={() => handleParameterChange('pm10')}
          >
            PM10
          </button>
          <button 
            className={`control-btn ${activeParameter === 'no2' ? 'active' : ''}`}
            onClick={() => handleParameterChange('no2')}
          >
            NO<sub>2</sub>
          </button>
          <button 
            className={`control-btn ${activeParameter === 'so2' ? 'active' : ''}`}
            onClick={() => handleParameterChange('so2')}
          >
            SO<sub>2</sub>
          </button>
          <button 
            className={`control-btn ${activeParameter === 'o3' ? 'active' : ''}`}
            onClick={() => handleParameterChange('o3')}
          >
            O<sub>3</sub>
          </button>
        </div>
        
        <div className="timeframe-controls">
          <button 
            className={`control-btn ${activeTimeframe === '24h' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('24h')}
          >
            24 Saat
          </button>
          <button 
            className={`control-btn ${activeTimeframe === '7d' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('7d')}
          >
            7 Gün
          </button>
          <button 
            className={`control-btn ${activeTimeframe === '30d' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('30d')}
          >
            30 Gün
          </button>
        </div>
      </div>
      
      <div className="chart-container">
        {hasData ? (
          <Line data={chartData} options={options} />
        ) : (
          <div className="no-data">
            <div className="no-data-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 3v18h18"></path>
                <path d="m19 9-5 5-4-4-3 3"></path>
              </svg>
            </div>
            <p>Seçilen parametre ve zaman aralığı için veri bulunmamaktadır.<br />Lütfen farklı bir parametre veya zaman aralığı seçin.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrendChart; 