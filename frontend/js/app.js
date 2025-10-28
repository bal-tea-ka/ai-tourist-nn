// Основная логика приложения
document.addEventListener('DOMContentLoaded', () => {
console.log('🚀 AI Tourist Assistant загружен');

text
// Инициализация карты
if (typeof ymaps !== 'undefined') {
    MapModule.init();
} else {
    console.error('Яндекс.Карты не загружены. Проверьте API ключ.');
}

// Обработка слайдера времени
const timeSlider = document.getElementById('time');
const timeValue = document.getElementById('timeValue');

timeSlider.addEventListener('input', (e) => {
    timeValue.textContent = e.target.value;
});

// Обработка отправки формы
const form = document.getElementById('routeForm');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleFormSubmit();
});
});

async function handleFormSubmit() {
UI.hideResult();
UI.showLoading(true);

text
try {
    const interests = document.getElementById('interests').value;
    const time = parseInt(document.getElementById('time').value);
    const address = document.getElementById('address').value;
    
    // Геокодирование адреса
    console.log('Геокодирование адреса:', address);
    const location = await Geocoder.geocode(+"Нижний Новгород, "+);
    console.log('Координаты получены:', location);
    
    // Формирование запроса
    const requestData = {
        user_interests: interests,
        available_time_hours: time,
        user_location: {
            address: location.address,
            latitude: location.latitude,
            longitude: location.longitude
        }
    };
    
    // Отправка запроса к API
    console.log('Отправка запроса к API:', requestData);
    const result = await API.generateRoute(requestData);
    console.log('Получен ответ:', result);
    
    // Построение маршрута на карте
    MapModule.buildRoute([
        { latitude: location.latitude, longitude: location.longitude, title: 'Старт' },
        ...result.route.places.map(p => ({
            latitude: parseFloat(p.coordinates.latitude),
            longitude: parseFloat(p.coordinates.longitude),
            title: p.title,
            address: p.address
        }))
    ]);
    
    // Отображение результата
    UI.showResult(result);
    
} catch (error) {
    console.error('Ошибка:', error);
    UI.showError(error.message || 'Произошла ошибка при генерации маршрута');
} finally {
    UI.showLoading(false);
}
}
