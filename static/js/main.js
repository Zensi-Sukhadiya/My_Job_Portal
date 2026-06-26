//Footer Back to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // smooth scroll
    });
}


// Aleart Message
function dismissAlert(id) {
    const alert = document.getElementById(id);
    if (alert) {
        alert.classList.add('fade-out');
        setTimeout(() => {
            alert.remove();
        }, 300);
    }
}

// Auto-dismiss after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            dismissAlert(alert.id);
        }, 5000 + (index * 200));
    });
});
