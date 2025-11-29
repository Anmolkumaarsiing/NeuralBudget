document.addEventListener('DOMContentLoaded', function() {
    fetchSpendingInsights();
});

async function fetchSpendingInsights() {
    const insightsContainer = document.getElementById('insights-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsContent = document.getElementById('results-content');

    loadingSpinner.style.display = 'block';
    resultsContent.style.display = 'none';
    resultsContent.innerHTML = ''; // Clear previous content

    try {
        const response = await fetch('/insights/api/get-spending-insights/');
        const data = await response.json();

        if (response.ok) {
            displayInsights(data);
        } else {
            displayError(data.error || 'Failed to fetch spending insights.');
        }
    } catch (error) {
        console.error('Error fetching spending insights:', error);
        displayError('An unexpected error occurred. Please try again.');
    } finally {
        loadingSpinner.style.display = 'none';
        resultsContent.style.display = 'block';
    }
}

function displayInsights(data) {
    const resultsContent = document.getElementById('results-content');

    // Summary
    resultsContent.innerHTML += `
        <div class="insight-section-header">
            <i class="fas fa-chart-pie"></i>
            <h2>Spending Summary</h2>
        </div>
        <p class="summary-text">${data.summary}</p>
    `;

    // Insights
    resultsContent.innerHTML += `
        <div class="insight-section-header">
            <i class="fas fa-lightbulb"></i>
            <h2>Key Insights</h2>
        </div>
        <div class="insights-grid">
            ${data.insights.map(insight => `
                <div class="insight-card">
                    <div class="card-icon">
                        <i class="fas ${insight.icon}"></i>
                    </div>
                    <div class="card-content">
                        <h3>${insight.title}</h3>
                        <p>${insight.description}</p>
                        <p class="suggestion"><strong>Suggestion:</strong> ${insight.suggestion}</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    // Top Categories (optional, if you want a chart here)
    if (data.top_categories && data.top_categories.length > 0) {
        resultsContent.innerHTML += `
            <div class="insight-section-header">
                <i class="fas fa-tags"></i>
                <h2>Top Spending Categories (Last 30 Days)</h2>
            </div>
            <div class="category-list">
                ${data.top_categories.map(category => `
                    <div class="category-item">
                        <span>${category.name}</span>
                        <span>₹${category.amount.toFixed(2)} (${category.percentage.toFixed(2)}%)</span>
                    </div>
                `).join('')}
            </div>
            <canvas id="topCategoriesChart" width="400" height="200"></canvas>
        `;
        renderTopCategoriesChart(data.top_categories);
    }
}

function displayError(message) {
    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <p>Please try reloading the page or check back later.</p>
        </div>
    `;
}

function renderTopCategoriesChart(categories) {
    const ctx = document.getElementById('topCategoriesChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: categories.map(c => c.name),
            datasets: [{
                data: categories.map(c => c.amount),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#E7E9ED', '#8D6E63', '#4DD0E1', '#FFD54F'
                ],
                hoverBackgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                    '#FF9F40', '#E7E9ED', '#8D6E63', '#4DD0E1', '#FFD54F'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'right',
            },
            title: {
                display: false,
                text: 'Top Spending Categories'
            }
        }
    });
}
