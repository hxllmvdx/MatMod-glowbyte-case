import { useState } from 'react';
import './Calendar.css';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState(null);

  const daysInMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1,
    0
  ).getDate();

  const firstDayOfMonth = new Date(
    currentDate.getFullYear(),
    currentDate.getMonth(),
    1
  ).getDay();

  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
    setSelectedDay(null); // Сбрасываем выбранный день при смене месяца
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
    setSelectedDay(null); // Сбрасываем выбранный день при смене месяца
  };

  const handleDayClick = (day) => {
    if (selectedDay === day) {
      // Если кликнули на уже выбранный день - отменяем выбор
      setSelectedDay(null);
    } else {
      setSelectedDay(day);
    }
  };

  // Фиксируем статусы дней, чтобы они не менялись при перерисовке
  const getStatuses = () => {
    const statuses = {};
    const seed = currentDate.getFullYear() * 100 + currentDate.getMonth();
    
    for (let day = 1; day <= daysInMonth; day++) {
      // Используем детерминированное псевдослучайное число на основе дня и месяца
      const random = ((seed * day) % 100) / 100;
      if (random < 0.3) statuses[day] = 'fire';
      else if (random < 0.6) statuses[day] = 'safe';
      else statuses[day] = 'risk';
    }
    
    return statuses;
  };
  
  const dayStatuses = getStatuses();

  const renderCalendarDays = () => {
    const days = [];
    const totalDays = 42; // 6 недель * 7 дней

    // Добавляем пустые ячейки для выравнивания
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Добавляем дни месяца
    for (let day = 1; day <= daysInMonth; day++) {
      const status = dayStatuses[day];
      days.push(
        <div
          key={day}
          className={`calendar-day ${status} ${selectedDay === day ? 'selected' : ''}`}
          onClick={() => handleDayClick(day)}
        >
          {day}
        </div>
      );
    }

    // Добавляем оставшиеся пустые ячейки
    const remainingDays = totalDays - (firstDayOfMonth + daysInMonth);
    for (let i = 0; i < remainingDays; i++) {
      days.push(<div key={`empty-end-${i}`} className="calendar-day empty"></div>);
    }

    return days;
  };

  return (
    <div className={`calendar ${selectedDay ? 'with-selected-day' : ''}`}>
      <div className="calendar-header">
        <button className="calendar-nav-btn" onClick={handlePrevMonth}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <h2 className="calendar-title">
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h2>
        <button className="calendar-nav-btn" onClick={handleNextMonth}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      <div className="calendar-weekdays">
        <div className="weekday">Пн</div>
        <div className="weekday">Вт</div>
        <div className="weekday">Ср</div>
        <div className="weekday">Чт</div>
        <div className="weekday">Пт</div>
        <div className="weekday">Сб</div>
        <div className="weekday">Вс</div>
      </div>

      <div className="calendar-grid">
        {renderCalendarDays()}
      </div>

      {selectedDay && (
        <div className="day-info">
          <h3>Информация за {selectedDay} {monthNames[currentDate.getMonth()]}</h3>
          <div className="day-status">
            <span className={`status-indicator ${dayStatuses[selectedDay]}`}></span>
            <span>
              {dayStatuses[selectedDay] === 'fire' && 'Зафиксировано возгорание'}
              {dayStatuses[selectedDay] === 'safe' && 'Возгораний не зафиксировано'}
              {dayStatuses[selectedDay] === 'risk' && 'Повышенный риск возгорания'}
            </span>
          </div>
          <div className="day-details">
            <p>Температура: 25°C</p>
            <p>Влажность: 45%</p>
            <p>Скорость ветра: 5 м/с</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar; 