/**
 * Модуль для безопасной работы с Яндекс.Картами
 */

let map = null;
let routePolyline = null;
let placemarks = [];
let userLocationMark = null;

/**
 * Загрузить конфигурацию карты с backend
 */
async function loadMapConfig() {
    try {
        const response = await fetch('http://localhost:8000/api/maps/config');
        if (!response.ok) throw new Error('Failed to load map config');
        return await response.json();
    } catch (error) {
        console.error('Ошибка загрузки конфигурации карты:', error);
        return null;
    }
}

/**
 * Динамически загрузить Яндекс.Карты API
 */
async function loadYandexMapsAPI() {
    const config = await loadMapConfig();
    
    if (!config) {
        console.error('Не удалось загрузить конфигурацию карты');
        return false;
    }
    
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = `https://api-maps.yandex.ru/2.1/?apikey=${config.api_key}&lang=ru_RU`;
        script.onload = () => resolve(config);
        script.onerror = () => reject(new Error('Failed to load Yandex Maps API'));
        document.head.appendChild(script);
    });
}

/**
 * Инициализация карты
 */
function initMap() {
    const centerCoords = [56.3287, 44.0020];
    
    map = new ymaps.Map('map', {
        center: centerCoords,
        zoom: 12,
        controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
    });
}

/**
 * Очистить карту от предыдущих меток и маршрутов
 */
function clearMap() {
    if (!map) return;
    
    placemarks.forEach(placemark => map.geoObjects.remove(placemark));
    placemarks = [];
    
    if (routePolyline) {
        map.geoObjects.remove(routePolyline);
        routePolyline = null;
    }
}

/**
 * Отобразить маршрут на карте
 */
function displayRoute(routeData) {
    if (!map) {
        console.error('Карта не инициализирована');
        return;
    }
    
    clearMap();
    
    const places = routeData.places;
    if (!places || places.length === 0) {
        console.warn('Нет мест для отображения');
        return;
    }
    
    const coordinates = [];
    
    places.forEach((place, index) => {
        const coords = [place.coordinates.latitude, place.coordinates.longitude];
        coordinates.push(coords);
        
        const placemark = new ymaps.Placemark(coords, {
            balloonContentHeader: `<strong>${index + 1}. ${place.title}</strong>`,
            balloonContentBody: `
                <p><strong>Категория:</strong> ${place.category.name}</p>
                <p><strong>Адрес:</strong> ${place.address}</p>
                <p><strong>Время посещения:</strong> ${place.visit_duration} мин</p>
                <p><strong>Расстояние:</strong> ${place.distance_from_user} км</p>
                <p class="small">${place.description}</p>
            `,
            hintContent: place.title
        }, {
            preset: 'islands#blueCircleDotIcon',
            iconContentLayout: ymaps.templateLayoutFactory.createClass(
                `<div style="color: white; font-weight: bold;">${index + 1}</div>`
            )
        });
        
        map.geoObjects.add(placemark);
        placemarks.push(placemark);
    });
    
    if (coordinates.length > 1) {
        routePolyline = new ymaps.Polyline(coordinates, {}, {
            strokeColor: '#0066ff',
            strokeWidth: 4,
            strokeOpacity: 0.7
        });
        
        map.geoObjects.add(routePolyline);
    }
    
    map.setBounds(map.geoObjects.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50
    });
}

/**
 * Показать местоположение пользователя
 */
function showUserLocation(latitude, longitude) {
    if (!map) return;
    
    if (userLocationMark) {
        map.geoObjects.remove(userLocationMark);
    }
    
    userLocationMark = new ymaps.Placemark([latitude, longitude], {
        hintContent: 'Ваше местоположение',
        balloonContent: 'Вы находитесь здесь'
    }, {
        preset: 'islands#redHomeIcon'
    });
    
    map.geoObjects.add(userLocationMark);
}

/**
 * Геокодирование адреса через backend
 */
async function geocodeAddress(address) {
    try {
        const response = await fetch('http://localhost:8000/api/maps/geocode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address })
        });
        
        if (!response.ok) {
            throw new Error('Geocoding failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка геокодирования:', error);
        return null;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const config = await loadYandexMapsAPI();
        if (config) {
            ymaps.ready(initMap);
        }
    } catch (error) {
        console.error('Ошибка инициализации карт:', error);
    }
});
