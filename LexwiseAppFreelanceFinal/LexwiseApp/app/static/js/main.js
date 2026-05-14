// Main JavaScript file for LexWise
console.log('LexWise loaded');

// CSRF token handling
function getCsrfToken() {
    return document.querySelector('input[name="csrf_token"]')?.value || '';
}

// Auto-hide flash messages
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);