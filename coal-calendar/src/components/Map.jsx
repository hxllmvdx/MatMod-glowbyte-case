import { useState, useEffect } from 'react';
import './Map.css';

const Map = () => {
  const [mapData, setMapData] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(null);

  useEffect(() => {
    // Здесь будет загрузка данных карты
    // Временные данные для демонстрации
    const mockData = {
      points: [
        { id: 1, x: 30, y: 40, status: 'fire', temperature: 35, humidity: 30, windSpeed: 8 },
        { id: 2, x: 60, y: 70, status: 'safe', temperature: 25, humidity: 45, windSpeed: 5 },
        { id: 3, x: 80, y: 20, status: 'risk', temperature: 30, humidity: 35, windSpeed: 12 },
      ]
    };
    setMapData(mockData);
  }, []);

  const handlePointClick = (point) => {
    if (selectedPoint && selectedPoint.id === point.id) {
      // If clicking on the same point, deselect it
      setSelectedPoint(null);
    } else {
      // Otherwise, select the new point
      setSelectedPoint(point);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'fire':
        return '#ff0000';
      case 'safe':
        return '#00ff00';
      case 'risk':
        return '#ffff00';
      default:
        return '#808080';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'fire':
        return 'Зафиксировано возгорание';
      case 'safe':
        return 'Возгораний не зафиксировано';
      case 'risk':
        return 'Повышенный риск возгорания';
      default:
        return 'Статус неизвестен';
    }
  };

  return (
    <div className="map-container">
      <div className="map">
        {mapData?.points.map((point) => (
          <div
            key={point.id}
            className="map-point"
            style={{
              left: `${point.x}%`,
              top: `${point.y}%`,
              backgroundColor: getStatusColor(point.status)
            }}
            onClick={() => handlePointClick(point)}
          />
        ))}
      </div>

      {selectedPoint && (
        <div className="point-info">
          <h3>Информация о точке</h3>
          <div className="point-status">
            <span
              className="status-indicator"
              style={{ backgroundColor: getStatusColor(selectedPoint.status) }}
            />
            <span>{getStatusText(selectedPoint.status)}</span>
          </div>
          <div className="point-details">
            <p>Температура: {selectedPoint.temperature}°C</p>
            <p>Влажность: {selectedPoint.humidity}%</p>
            <p>Скорость ветра: {selectedPoint.windSpeed} м/с</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Map; 