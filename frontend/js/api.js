const API = {
    generateRoute: async function(data) {
        const url = CONFIG.API_BASE_URL + '/route/generate';
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка API');
        }
        
        return await response.json();
    }
};
