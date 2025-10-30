/**
 * Главный файл приложения с анимациями 
 */

document.getElementById('routeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const interests = document.getElementById('interests').value;
    const time = parseInt(document.getElementById('time').value);
    const address = document.getElementById('address').value;

    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Определяем координаты...';

    try {
        // Запрашиваем координаты у backend по адресу
        const geocodeResponse = await fetch('http://localhost:8000/api/maps/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: address })
        });

        if (!geocodeResponse.ok) {
            throw new Error('Не удалось определить координаты');
        }

        const geocodeResult = await geocodeResponse.json();

        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Генерируем маршрут...';

        if (typeof showUserLocation === 'function') {
            showUserLocation(geocodeResult.latitude, geocodeResult.longitude);
        }

        const response = await fetch('http://localhost:8000/api/route/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
            user_interests: interests,
            available_time_hours: time,
            user_location: {
                address: geocodeResult.formatted_address,
                latitude: geocodeResult.latitude,
                longitude: geocodeResult.longitude
            }
            }),

        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('mapContainer').style.display = 'block';
            displayRoute(data.route);
            displayResults(data);

            setTimeout(() => {
                document.getElementById('mapContainer').scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 300);
        } else {
            showError('Ошибка при генерации маршрута');
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
        showError(error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});



function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    if (!data.route.places || data.route.places.length === 0) {
        resultsDiv.innerHTML = `
            <div class="alert alert-warning fade-in">
                <i class="bi bi-exclamation-triangle"></i> 
                Не удалось построить маршрут. Попробуйте изменить параметры.
            </div>
        `;
        return;
    }
    
    const categoryIcons = {
        1: '🗿', 2: '🌳', 3: '👋', 4: '🌊', 5: '🏛️',
        6: '🎭', 7: '🖼️', 8: '🎪', 9: '🎨'
    };
    
    let html = `
        <div class="card shadow-lg mb-4 fade-in">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <i class="bi bi-check-circle"></i> Маршрут построен успешно!
                </h5>
            </div>
            <div class="card-body">
                <div class="row text-center mb-4">
                    <div class="col-md-3 mb-3">
                        <div class="stat-card p-3">
                            <i class="bi bi-geo-alt-fill text-primary" style="font-size: 2rem;"></i>
                            <h6 class="text-muted mt-2 mb-1">Мест</h6>
                            <p class="stat-number mb-0">${data.route.total_places}</p>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card p-3">
                            <i class="bi bi-clock-fill text-info" style="font-size: 2rem;"></i>
                            <h6 class="text-muted mt-2 mb-1">Время</h6>
                            <p class="stat-number mb-0">${data.route.total_time_minutes}</p>
                            <small class="text-muted">минут</small>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card p-3">
                            <i class="bi bi-signpost-fill text-warning" style="font-size: 2rem;"></i>
                            <h6 class="text-muted mt-2 mb-1">Расстояние</h6>
                            <p class="stat-number mb-0">${data.route.total_distance_km}</p>
                            <small class="text-muted">км</small>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="stat-card p-3">
                            <i class="bi bi-person-walking text-success" style="font-size: 2rem;"></i>
                            <h6 class="text-muted mt-2 mb-1">Пешком</h6>
                            <p class="stat-number mb-0">${data.route.walking_time_minutes}</p>
                            <small class="text-muted">минут</small>
                        </div>
                    </div>
                </div>
                
                <h6 class="mt-4 mb-3">
                    <i class="bi bi-list-ol"></i> Места для посещения:
                </h6>
                <div class="list-group">
    `;
    
    data.route.places.forEach((place, index) => {
        const icon = categoryIcons[place.category.id] || '📍';
        html += `
            <div class="list-group-item fade-in" style="animation-delay: ${index * 0.1}s">
                <div class="d-flex w-100 justify-content-between align-items-start mb-2">
                    <h6 class="mb-1">
                        <span class="badge bg-primary me-2">${index + 1}</span>
                        ${icon} ${place.title}
                    </h6>
                    <span class="badge bg-info">${place.visit_duration} мин</span>
                </div>
                <p class="mb-1">
                    <i class="bi bi-tag-fill text-primary"></i> 
                    <small><strong>Категория:</strong> ${place.category.name}</small>
                </p>
                <p class="mb-1">
                    <i class="bi bi-geo-alt-fill text-danger"></i> 
                    <small><strong>Адрес:</strong> ${place.address}</small>
                </p>
                <p class="mb-2">
                    <i class="bi bi-arrow-right-circle-fill text-success"></i> 
                    <small><strong>Расстояние:</strong> ${place.distance_from_user} км</small>
                </p>
                <p class="mb-0 small text-muted">${place.description}</p>
            </div>
        `;
    });
    
    html += `
                </div>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="alert alert-danger fade-in">
            <i class="bi bi-exclamation-triangle-fill"></i> 
            <strong>Ошибка:</strong> ${message}
        </div>
    `;
}
