// Модуль управления UI
const UI = {
showLoading(show) {
const btn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');

text
    if (show) {
        btn.disabled = true;
        btnText.textContent = 'Генерация маршрута...';
        btnSpinner.classList.remove('d-none');
    } else {
        btn.disabled = false;
        btnText.textContent = 'Построить маршрут';
        btnSpinner.classList.add('d-none');
    }
},

showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
    
    setTimeout(() => {
        errorDiv.classList.add('d-none');
    }, 5000);
},

showResult(routeData) {
    const resultDiv = document.getElementById('result');
    const routeInfoDiv = document.getElementById('routeInfo');
    const placesListDiv = document.getElementById('placesList');
    
    // Информация о маршруте
    routeInfoDiv.innerHTML = +"
        <strong>Маршрут построен!</strong><br>
        📍 Мест в маршруте: <br>
        ⏱️ Общее время:  минут<br>
        🚶 Расстояние:  км
    "+;
    
    // Список мест
    placesListDiv.innerHTML = '';
    routeData.route.places.forEach((place, index) => {
        const placeCard = +"
            <div class=\"col-md-6 place-card\">
                <div class=\"card\">
                    <div class=\"card-body\">
                        <h5 class=\"card-title\">
                            <span class=\"place-number\"></span>
                            
                        </h5>
                        <p class=\"text-muted mb-2\"></p>
                        <span class=\"place-category\"></span>
                        <p class=\"mt-2\">...</p>
                        <div class=\"place-duration\">
                            ⏱️  минут
                        </div>
                        </small></div>"+ : ''}
                    </div>
                </div>
            </div>
        "+;
        placesListDiv.innerHTML += placeCard;
    });
    
    resultDiv.classList.remove('d-none');
},

hideResult() {
    document.getElementById('result').classList.add('d-none');
}
};
