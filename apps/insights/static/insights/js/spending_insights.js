document.addEventListener('DOMContentLoaded', async () => {
    const spinner = document.getElementById('loading-spinner');
    const resultsContent = document.getElementById('results-content');

    try {
        // Fetch the data from the new API endpoint
        const response = await fetch('/insights/api/get-spending-insights/');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get insights.');
        }
        
        renderInsights(data);
        resultsContent.style.display = 'block'; // Show the results container

    } catch (error) {
        resultsContent.innerHTML = `<div class="error-container"><h3>Analysis Failed</h3><p>${error.message}</p></div>`;
        resultsContent.style.display = 'block';
    } finally {
        spinner.style.display = 'none'; // Hide the spinner
    }
});

function renderInsights(insights) {
    const resultsContent = document.getElementById('results-content');
    // Dynamically build the HTML for the insight cards
    resultsContent.innerHTML = `
        <div class="insights-grid">
            <div class="insight-card">
                <div class="card-icon habit-icon"><i class="fas fa-search-dollar"></i></div>
                <div class="card-content">
                    <h4>Your Spending Habit</h4>
                    <p>${insights.spending_habit}</p>
                </div>
            </div>
            <div class="insight-card">
                <div class="card-icon savings-icon"><i class="fas fa-lightbulb"></i></div>
                <div class="card-content">
                    <h4>SAVI's Suggestion</h4>
                    <p>${insights.savings_suggestion}</p>
                </div>
            </div>
            <div class="insight-card">
                <div class="card-icon purchase-icon"><i class="fas fa-receipt"></i></div>
                <div class="card-content">
                    <h4>Largest Purchase</h4>
                    <p>"${insights.largest_purchase.name}"</p>
                    <span class="large-purchase-amount">₹${insights.largest_purchase.amount.toFixed(2)}</span>
                </div>
            </div>
        </div>
    `;
}