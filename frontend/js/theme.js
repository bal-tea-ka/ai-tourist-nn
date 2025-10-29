/**
 * Переключение светлой и темной темы с динамическими текстами
 */

// Получаем сохранённую тему из localStorage или используем светлую по умолчанию
const currentTheme = localStorage.getItem('theme') || 'light';

// Применяем тему при загрузке страницы
document.documentElement.setAttribute('data-theme', currentTheme);

// Обновляем UI при загрузке
window.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeToggle) {
        themeToggle.checked = currentTheme === 'dark';
        updateThemeIcon(currentTheme);
        
        // Обработчик переключения
        themeToggle.addEventListener('change', function() {
            const theme = this.checked ? 'dark' : 'light';
            setTheme(theme);
        });
    }
    
    // Обновляем мобильное меню
    updateMobileThemeText(currentTheme);
});

/**
 * Установить тему
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
    updateMobileThemeText(theme);
}

/**
 * Обновить иконку в toggle-переключателе
 */
function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill';
        } else {
            themeIcon.className = 'bi bi-moon-fill';
        }
    }
}

/**
 * Обновить текст и иконку в мобильном меню
 */
function updateMobileThemeText(theme) {
    const mobileThemeLink = document.getElementById('mobileThemeToggle');
    const mobileThemeIcon = document.getElementById('mobileThemeIcon');
    const mobileThemeText = document.getElementById('mobileThemeText');
    
    if (theme === 'dark') {
        // Сейчас темная тема, предлагаем переключить на светлую
        if (mobileThemeIcon) {
            mobileThemeIcon.className = 'bi bi-sun';
        }
        if (mobileThemeText) {
            mobileThemeText.textContent = 'Светлая тема';
        }
    } else {
        // Сейчас светлая тема, предлагаем переключить на темную
        if (mobileThemeIcon) {
            mobileThemeIcon.className = 'bi bi-moon-stars';
        }
        if (mobileThemeText) {
            mobileThemeText.textContent = 'Темная тема';
        }
    }
}

/**
 * Переключение темы для мобильной версии
 */
function toggleThemeMobile() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Обновляем чекбокс если есть
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.checked = newTheme === 'dark';
    }
}
