// Language system
let currentLang = 'es';

function toggleLanguage() {
    currentLang = currentLang === 'es' ? 'en' : 'es';
    updateLanguage();
    localStorage.setItem('language', currentLang);
}

function updateLanguage() {
    document.querySelectorAll('[data-lang]').forEach(element => {
        element.style.display = element.getAttribute('data-lang') === currentLang ? 'inline' : 'none';
    });
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedLang = localStorage.getItem('language');
    if (savedLang) {
        currentLang = savedLang;
        updateLanguage();
    }
});