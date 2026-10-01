/* ==========================================================================
   Expense Tracker Management System - Global Main JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Theme Switcher Logic
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isLight = document.body.classList.toggle('light-theme');
            const icon = themeToggleBtn.querySelector('i');
            if (isLight) {
                icon.className = 'fas fa-sun';
                localStorage.setItem('expense_tracker_theme', 'light');
            } else {
                icon.className = 'fas fa-moon';
                localStorage.setItem('expense_tracker_theme', 'dark');
            }
        });

        // Apply saved theme on load
        const savedTheme = localStorage.getItem('expense_tracker_theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
            const icon = themeToggleBtn.querySelector('i');
            if (icon) icon.className = 'fas fa-sun';
        }
    }

    // Auto-dismiss alerts after 5s
    const alerts = document.querySelectorAll('.alert-box');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });
});

// Format Currency Utility
function formatCurrency(amount, symbol = '₹') {
    return `${symbol}${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
