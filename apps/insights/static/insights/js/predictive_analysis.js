document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement) {
        console.error('Chart data not found in the template.');
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    // Render Forecast Chart (Bar Chart)
    if (chartData.forecast_chart) {
        const forecastCtx = document.getElementById('forecast-chart').getContext('2d');
        new Chart(forecastCtx, {
            type: 'bar',
            data: {
                labels: chartData.forecast_chart.labels,
                datasets: [{
                    label: 'Spending (₹)',
                    data: chartData.forecast_chart.values,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // Render Category Chart (Doughnut Chart)
    if (chartData.category_chart) {
        const categoryCtx = document.getElementById('category-chart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: chartData.category_chart.labels,
                datasets: [{
                    label: 'Spend by Category',
                    data: chartData.category_chart.values,
                    backgroundColor: [
                        '#24a791', '#4f46e5', '#f59e0b', '#ef4444', '#3b82f6'
                    ],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    }
});