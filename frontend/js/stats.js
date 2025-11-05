/**
 * Статистика использования сервиса
 */

// Загрузка статистики при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    await loadCategoryStats();
    
    // Обновляем статистику каждые 30 секунд
    setInterval(loadStats, 30000);
});

/**
 * Загрузить общую статистику
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Основные метрики
        document.getElementById('totalRequests').textContent = data.total_requests;
        document.getElementById('recentRequests').textContent = data.recent_requests_24h;
        document.getElementById('avgTime').textContent = data.averages.time_minutes.toFixed(0);
        document.getElementById('avgDistance').textContent = data.averages.distance_km.toFixed(1);
        document.getElementById('avgPlaces').textContent = data.averages.places_per_route.toFixed(1);
        document.getElementById('avgExecution').textContent = data.averages.execution_time_ms.toFixed(0);
        
        // Популярные интересы
        displayPopularInterests(data.popular_interests);
        
        // Популярные локации
        displayPopularLocations(data.popular_locations);
        
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

/**
 * Отобразить популярные интересы
 */
function displayPopularInterests(interests) {
    const container = document.getElementById('popularInterests');
    
    if (!interests || interests.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Нет данных</p>';
        return;
    }
    
    let html = '<div class="list-group">';
    
    interests.slice(0, 5).forEach((item, index) => {
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <span><strong>${index + 1}.</strong> ${item.interests}</span>
                <span class="badge bg-primary rounded-pill">${item.count}</span>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Отобразить популярные локации
 */
function displayPopularLocations(locations) {
    const container = document.getElementById('popularLocations');
    
    if (!locations || locations.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Нет данных</p>';
        return;
    }
    
    let html = '<div class="row">';
    
    locations.slice(0, 6).forEach((item, index) => {
        html += `
            <div class="col-md-6 mb-2">
                <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                    <span class="text-truncate"><strong>${index + 1}.</strong> ${item.address}</span>
                    <span class="badge bg-info ms-2">${item.count}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Загрузить статистику по категориям
 */
async function loadCategoryStats() {
    try {
        const response = await fetch('/api/stats/categories');
        const data = await response.json();
        
        displayCategoryStats(data.categories);
        
    } catch (error) {
        console.error('Ошибка загрузки статистики категорий:', error);
    }
}

/**
 * Отобразить статистику категорий
 */
function displayCategoryStats(categories) {
    const container = document.getElementById('categoryStats');
    
    if (!categories || categories.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Нет данных</p>';
        return;
    }
    
    // Находим максимальное значение для прогресс-баров
    const maxUsage = Math.max(...categories.map(c => c.usage_count));
    
    let html = '';
    
    categories.forEach(cat => {
        const percentage = maxUsage > 0 ? (cat.usage_count / maxUsage * 100) : 0;
        
        html += `
            <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                    <span><strong>${cat.category_name}</strong></span>
                    <span class="text-muted">${cat.usage_count} раз</span>
                </div>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar bg-warning" role="progressbar" 
                         style="width: ${percentage}%" 
                         aria-valuenow="${cat.usage_count}" 
                         aria-valuemin="0" 
                         aria-valuemax="${maxUsage}">
                        ${cat.usage_count > 0 ? cat.usage_count : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}
