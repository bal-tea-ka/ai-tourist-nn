document.addEventListener('DOMContentLoaded', function() {
    console.log('Приложение загружено');
    
    const timeSlider = document.getElementById('time');
    const timeValue = document.getElementById('timeValue');
    
    if (timeSlider && timeValue) {
        timeSlider.addEventListener('input', function(e) {
            timeValue.textContent = e.target.value;
        });
    }
    
    const form = document.getElementById('routeForm');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const interests = document.getElementById('interests').value;
            const time = document.getElementById('time').value;
            const address = document.getElementById('address').value;
            
            console.log('Форма отправлена');
            console.log('Интересы:', interests);
            console.log('Время:', time);
            console.log('Адрес:', address);
            
            alert('Данные: ' + interests + ', ' + time + ' ч, ' + address);
        });
    }
});
