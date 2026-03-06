document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
});

function showAlert(message) {
    const alertHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            ${message} section loaded successfully!
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHTML);
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }
}

console.log('BNM Assessment Dashboard ready');