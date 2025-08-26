document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/datagen/api/get-admin-analytics/');
        if (!response.ok) {
            throw new Error('Failed to fetch analytics data.');
        }
        const data = await response.json();

        // Populate KPI Cards
        document.getElementById('total-users').textContent = data.total_users;
        document.getElementById('new-users').textContent = data.new_users_last_7_days;

        // Render Top Categories Chart
        const ctx = document.getElementById('top-categories-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.top_categories_chart.labels,
                datasets: [{
                    label: 'Total Spend (₹)',
                    data: data.top_categories_chart.values,
                    backgroundColor: 'rgba(79, 70, 229, 0.8)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 1,
                    borderRadius: 5
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });

    } catch (error) {
        console.error("Error loading dashboard data:", error);
    }
});