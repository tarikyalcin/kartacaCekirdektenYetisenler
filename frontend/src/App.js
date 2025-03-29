import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Sayfaları buraya ekleyeceğiz
// import HomePage from './pages/HomePage';
// import MapPage from './pages/MapPage';
// import DetailPage from './pages/DetailPage';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          {/* <Route path="/" element={<HomePage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/detail/:location" element={<DetailPage />} />
          <Route path="*" element={<Navigate to="/" />} /> */}
          <Route path="/" element={<div>Hava Kirliliği İzleme Platformu - Geliştirme Aşamasında</div>} />
        </Routes>
      </Router>
    </div>
  );
}

export default App; 