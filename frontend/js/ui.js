const UI = {
    showLoading: function(show) {
        const btn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const btnSpinner = document.getElementById('btnSpinner');
        
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
    
    showError: function(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
        
        setTimeout(function() {
            errorDiv.classList.add('d-none');
        }, 5000);
    },
    
    hideResult: function() {
        const elem = document.getElementById('result');
        elem.classList.add('d-none');
    },
    
    showResult: function(data) {
        const resultDiv = document.getElementById('result');
        const routeInfo = document.getElementById('routeInfo');
        const placesList = document.getElementById('placesList');
        
        routeInfo.innerHTML = '<strong>Маршрут построен!</strong>';
        placesList.innerHTML = '';
        
        resultDiv.classList.remove('d-none');
    }
};
