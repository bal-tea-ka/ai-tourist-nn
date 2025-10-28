// API модуль для работы с backend
const API = {
async generateRoute(data) {
try {
const response = await fetch(+"/route/generate"+, {
method: 'POST',
headers: {
'Content-Type': 'application/json',
},
body: JSON.stringify(data)
});

text
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка генерации маршрута');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
},

async getCategories() {
    try {
        const response = await fetch(+"${CONFIG.API_BASE_URL}/categories"+);
        if (!response.ok) throw new Error('Ошибка загрузки категорий');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
},

async healthCheck() {
    try {
        const response = await fetch(+"${CONFIG.API_BASE_URL}/health"+);
        return await response.json();
    } catch (error) {
        console.error('Health check failed:', error);
        return { status: 'error' };
    }
}
};
