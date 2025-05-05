import { useState, useEffect } from 'react';
import sunIcon from './assets/sun.svg';
import moonIcon from './assets/moon.svg';
import glowbyteLogo from './assets/glowbyte.svg';
import Calendar from './components/Calendar';
import Map from './components/Map';
import './index.css';

const instructionMd = `- **Интерфейс**:
  - Шапка: "Добавить", переключение темы (солнце/луна).
  - Боковая панель: Карта, роза ветров, статистика.
  - Основное: Календарь (красный — возгорание, зелёный — нет, жёлтый — риск).
  - Подвал: Контакты, "О нас", инструкция.
- **Функции**:
  1. **Добавить данные**: "Добавить" → файлы/ввод → подтвердить.
  2. **Календарь**: Стрелки для месяцев, клик на день для инфо.
  3. **Дополнительные функции**: Переключение через боковую панель.`;

function App() {
  const [isDarkTheme, setIsDarkTheme] = useState(false);
  const [activeMenu, setActiveMenu] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showQrModal, setShowQrModal] = useState(false);
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [activePanel, setActivePanel] = useState(null); // 'map', 'wind' или 'stats'

  const qrCodes = [
    { 
      src: 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://t.me/SugarZhenia', 
      caption: 'Евгений\nФронтендер' 
    },
    { 
      src: 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://t.me/Girday', 
      caption: 'Максим\nФронтендер' 
    },
    { 
      src: 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://t.me/KR4K6', 
      caption: 'Андрей\nАналитик' 
    },
    { 
      src: 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://t.me/hxllmvdx', 
      caption: 'Матвей\nML-специалист' 
    },
    { 
      src: 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://t.me/tayaKU21', 
      caption: 'Тая\nБэкендер' 
    },
  ];

  useEffect(() => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDarkTheme(true);
      document.documentElement.classList.add('dark');
    }

    const handleClickOutside = (event) => {
      if (!event.target.closest('.footer-nav-item')) {
        setActiveMenu(null);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const toggleTheme = () => {
    setIsDarkTheme(!isDarkTheme);
    if (!isDarkTheme) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const toggleMenu = (menuName) => {
    if (activeMenu === menuName) {
      setActiveMenu(null);
    } else {
      setActiveMenu(menuName);
    }
  };

  const togglePanel = (panelName) => {
    if (activePanel === panelName) {
      setActivePanel(null);
    } else {
      setActivePanel(panelName);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    validateAndSetFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    validateAndSetFile(file);
  };

  const validateAndSetFile = (file) => {
    if (!file) return;
    
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setErrorMessage('Пожалуйста, выберите файл в формате CSV');
      setSelectedFile(null);
      return;
    }

    setErrorMessage('');
    setSelectedFile(file);
  };

  const uploadFile = () => {
    if (!selectedFile) return;
    console.log('Загрузка файла:', selectedFile.name);
    setShowUploadModal(false);
  };

  return (
    <div className="main-wrapper">
      <header className="main-header">
        <h1 className="main-title">Прогноз возгораний</h1>
        <div className="header-actions">
          <button className="header-btn" onClick={() => setShowUploadModal(true)}>
            <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Добавить
          </button>
          <button className="header-btn theme-toggle" onClick={toggleTheme}>
            <img src={isDarkTheme ? sunIcon : moonIcon} alt="Тема" width="30" height="30" />
          </button>
      </div>
      </header>

      <main className="main-content">
        <div className={`center-area ${activePanel ? 'has-side-panel' : ''}`}>
          <div className="side-buttons-mockup">
            <button 
              className={`side-btn-mockup ${activePanel === 'map' ? 'active' : ''}`}
              onClick={() => togglePanel('map')}
            >
              <svg width="59" height="59" viewBox="0 0 59 59" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" clipRule="evenodd" d="M58.3252 0.416035C58.5363 0.589111 58.7063 0.806906 58.823 1.0537C58.9397 1.30048 59.0002 1.57011 59 1.8431V53.4681C58.9997 53.8942 58.8519 54.307 58.5817 54.6364C58.3114 54.9658 57.9354 55.1915 57.5176 55.275L39.0801 58.9625C38.8416 59.0102 38.5959 59.0102 38.3574 58.9625L20.2812 55.3487L2.20512 58.9625C1.93774 59.0159 1.66183 59.0094 1.39727 58.9434C1.13271 58.8773 0.886091 58.7534 0.675179 58.5806C0.464266 58.4078 0.294312 58.1903 0.17756 57.9439C0.0608075 57.6975 0.000164657 57.4283 0 57.1556L0 5.5306C0.000257321 5.10452 0.148076 4.69168 0.418323 4.36228C0.688569 4.03287 1.06456 3.80723 1.48238 3.72372L19.9199 0.0362227C20.1584 -0.0114594 20.4041 -0.0114594 20.6426 0.0362227L38.7188 3.64997L56.7949 0.0362227C57.0622 -0.0175565 57.3381 -0.0113854 57.6027 0.0542914C57.8673 0.119968 58.1141 0.243516 58.3252 0.416035ZM36.875 7.04247L22.125 4.09247V51.9562L36.875 54.9062V7.04247ZM40.5625 54.9062L55.3125 51.9562V4.09247L40.5625 7.04247V54.9062ZM18.4375 51.9562V4.09247L3.6875 7.04247V54.9062L18.4375 51.9562Z" fill="currentColor"/>
              </svg>
            </button>
            <button 
              className={`side-btn-mockup ${activePanel === 'wind' ? 'active' : ''}`}
              onClick={() => togglePanel('wind')}
            >
              <svg width="70" height="70" viewBox="0 0 70 70" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g>
                  <path d="M34.9999 40.8334C36.547 40.8334 38.0307 40.2188 39.1247 39.1249C40.2187 38.0309 40.8332 36.5472 40.8332 35.0001C40.8332 33.453 40.2187 31.9693 39.1247 30.8753C38.0307 29.7813 36.547 29.1667 34.9999 29.1667C33.4528 29.1667 31.9691 29.7813 30.8751 30.8753C29.7812 31.9693 29.1666 33.453 29.1666 35.0001C29.1666 36.5472 29.7812 38.0309 30.8751 39.1249C31.9691 40.2188 33.4528 40.8334 34.9999 40.8334Z" stroke="currentColor" strokeWidth="2.81713" strokeMiterlimit="10"/>
                  <path d="M20.4167 34.9994H2.91667M67.0833 34.9994H49.5833M35 49.5828V67.0828M45.3133 45.3128L49.4375 49.4369M20.5625 20.5619L24.6896 24.6861M45.3133 24.6861L49.4375 20.5619M20.5625 49.4369L24.6896 45.3128M35 2.91611V20.4161" stroke="currentColor" strokeWidth="2.81713" strokeMiterlimit="10" strokeLinecap="round"/>
                </g>
              </svg>
            </button>
            <button 
              className={`side-btn-mockup ${activePanel === 'stats' ? 'active' : ''}`}
              onClick={() => togglePanel('stats')}
            >
              <svg width="58" height="58" viewBox="0 0 58 58" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g>
                  <path fillRule="evenodd" clipRule="evenodd" d="M0 0H3.625V54.375H58V58H0V0ZM53.7116 11.2846C53.896 11.4355 54.0488 11.6211 54.1613 11.8311C54.2738 12.041 54.3439 12.271 54.3674 12.508C54.391 12.745 54.3676 12.9844 54.2986 13.2123C54.2296 13.4403 54.1164 13.6524 53.9654 13.8366L37.6529 33.7741C37.4925 33.9698 37.293 34.1298 37.0671 34.2437C36.8413 34.3577 36.594 34.4231 36.3414 34.4357C36.0887 34.4483 35.8362 34.4079 35.6 34.3171C35.3639 34.2262 35.1494 34.087 34.9704 33.9082L25.5925 24.5304L12.3395 42.7533C12.0496 43.1219 11.6281 43.3638 11.1635 43.4282C10.6989 43.4925 10.2275 43.3743 9.8483 43.0983C9.46908 42.8224 9.2116 42.4102 9.12996 41.9483C9.04832 41.4865 9.14888 41.011 9.4105 40.6217L23.9105 20.6842C24.0644 20.4722 24.2624 20.2961 24.491 20.168C24.7195 20.0399 24.9731 19.9629 25.2342 19.9422C25.4954 19.9215 25.758 19.9577 26.0038 20.0483C26.2496 20.1388 26.4729 20.2816 26.6583 20.4667L36.1159 29.928L51.1596 11.5384C51.3105 11.354 51.4961 11.2012 51.7061 11.0887C51.916 10.9762 52.146 10.9061 52.383 10.8826C52.62 10.859 52.8594 10.8824 53.0873 10.9514C53.3153 11.0204 53.5275 11.1336 53.7116 11.2846Z" fill="currentColor"/>
                </g>
              </svg>
        </button>
          </div>
          <div className={`center-window ${activePanel ? 'with-side-panel' : ''}`}>
            <Calendar />
          </div>
          {activePanel && (
            <div className="side-panel">
              {activePanel === 'map' && (
                <div className="map-container">
                  <h3>Карта возгораний</h3>
                  <Map />
                </div>
              )}
              {activePanel === 'wind' && (
                <div className="wind-rose">
                  <h3>Роза ветров</h3>
                  <div className="wind-rose-content">
                    <div className="compass">
                      <div className="direction north">С</div>
                      <div className="direction east">В</div>
                      <div className="direction south">Ю</div>
                      <div className="direction west">З</div>
                      <div className="compass-arrow"></div>
                    </div>
                    <div className="wind-stats">
                      <p>Преобладающее направление: СВ</p>
                      <p>Средняя скорость: 5.2 м/с</p>
                      <p>Максимальная скорость: 12 м/с</p>
                    </div>
                  </div>
                </div>
              )}
              {activePanel === 'stats' && (
                <div className="statistics">
                  <h3>Статистика возгораний</h3>
                  <div className="stats-content">
                    <div className="stat-item">
                      <div className="stat-label">Всего пожаров</div>
                      <div className="stat-value">42</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Риск возгорания</div>
                      <div className="stat-value">Средний</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Дней без пожаров</div>
                      <div className="stat-value">14</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-label">Средняя температура</div>
                      <div className="stat-value">27°C</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <nav className="footer-nav">
          <div className="footer-nav-item">
            <a href="#" onClick={(e) => { e.preventDefault(); toggleMenu('contacts'); }}>Контакты</a>
            {activeMenu === 'contacts' && (
              <div className="context-menu menu-align-left">
                <div className="context-menu-item">Email: berezin.aw06@gmail.com</div>
                <div className="context-menu-item">Телефон: +7 (985) 215-47-85</div>
                <div className="context-menu-item">Git: https://github.com/hxllmvdx/MatMod-glowbyte-case.git</div>
              </div>
            )}
          </div>
          <div className="footer-nav-item">
            <a href="#" onClick={(e) => { e.preventDefault(); setShowQrModal(true); }}>О нас</a>
          </div>
          <div className="footer-nav-item">
            <a href="#" onClick={(e) => { e.preventDefault(); setShowInstructionModal(true); }}>Инструкция</a>
            {activeMenu === 'instructions' && (
              <div className="context-menu">
                <div className="context-menu-item">Начало работы</div>
                <div className="context-menu-item">Основные функции</div>
              </div>
            )}
          </div>
        </nav>
        <div className="footer-logo-copyright">
          <img src={glowbyteLogo} alt="GlowByte Logo" className="glowbyte-logo" />
          <span>© Copyright</span>
        </div>
      </footer>

      {/* Модальное окно загрузки */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Загрузка файла</h2>
              <button className="modal-close" onClick={() => setShowUploadModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div 
                className={`upload-area ${isDragging ? 'drag-over' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <input 
                  type="file" 
                  onChange={handleFileSelect} 
                  accept=".csv"
                  className="file-input"
                />
                <div className="upload-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                </div>
                <p className="upload-text">Перетащите CSV файл сюда или кликните для выбора</p>
                <p className="upload-hint">Поддерживаются только файлы формата .csv</p>
              </div>
              {selectedFile && (
                <div className="selected-file">
                  <p>Выбран файл: {selectedFile.name}</p>
                  <button className="upload-btn" onClick={uploadFile}>Загрузить</button>
                </div>
              )}
              {errorMessage && (
                <div className="error-message">
                  {errorMessage}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно с QR-кодами */}
      {showQrModal && (
        <div className="modal-overlay" onClick={() => setShowQrModal(false)}>
          <div className="modal-content qr-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Наши QR-коды</h2>
              <button className="modal-close" onClick={() => setShowQrModal(false)}>×</button>
            </div>
            <div className="modal-body qr-list">
              {qrCodes.map((qr, idx) => (
                <div key={idx} className="qr-item">
                  <img src={qr.src} alt={qr.caption} className="qr-img" />
                  <div className="qr-caption">{qr.caption}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно инструкции */}
      {showInstructionModal && (
        <div className="modal-overlay" onClick={() => setShowInstructionModal(false)}>
          <div className="modal-content instruction-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Краткая инструкция</h2>
              <button className="modal-close" onClick={() => setShowInstructionModal(false)}>×</button>
            </div>
            <div className="modal-body instruction-body">
              <ul>
                <li><strong>Интерфейс</strong>:
                  <ul>
                    <li>Шапка: "Добавить", переключение темы (солнце/луна).</li>
                    <li>Боковая панель: Карта, роза ветров, статистика.</li>
                    <li>Основное: Календарь (красный — возгорание, зелёный — нет, жёлтый — риск).</li>
                    <li>Подвал: Контакты, "О нас", инструкция.</li>
                  </ul>
                </li>
                <li><strong>Функции</strong>:
                  <ol>
                    <li><strong>Добавить данные</strong>: "Добавить" → файлы/ввод → подтвердить.</li>
                    <li><strong>Календарь</strong>: Стрелки для месяцев, клик на день для инфо.</li>
                    <li><strong>Дополнительные функции</strong>: Переключение через боковую панель.</li>
                  </ol>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
      </div>
  );
}

export default App;
