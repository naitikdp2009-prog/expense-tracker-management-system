/* ==========================================================================
   Expense Tracker Management System - Chart.js Renderers
   ========================================================================== */

let categoryDoughnutChart = null;
let trendLineChart = null;

function renderCategoryChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (categoryDoughnutChart) {
        categoryDoughnutChart.destroy();
    }

    categoryDoughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.length ? colors : ['#ef4444', '#f59e0b', '#ec4899', '#3b82f6', '#8b5cf6', '#10b981', '#06b6d4', '#14b8a6', '#6b7280'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12, weight: '600' },
                        padding: 14
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw || 0;
                            return ` ${context.label}: ₹${value.toLocaleString('en-IN')}`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

function renderTrendChart(canvasId, labels, expenseData, incomeData = []) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (trendLineChart) {
        trendLineChart.destroy();
    }

    const datasets = [
        {
            label: 'Expenses (₹)',
            data: expenseData,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#ef4444'
        }
    ];

    if (incomeData && incomeData.length > 0) {
        datasets.push({
            label: 'Income (₹)',
            data: incomeData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#10b981'
        });
    }

    trendLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#94a3b8', font: { size: 12, weight: '600' } }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}
