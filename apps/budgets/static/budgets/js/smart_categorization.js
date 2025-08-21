document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const spinner = document.getElementById('loading-spinner');
    const resultsContainer = document.getElementById('results-container');

    if (!analyzeBtn) {
        console.error("Analysis button not found! Make sure your button has id='analyze-btn'");
        return;
    }

    analyzeBtn.addEventListener('click', async () => {
        resultsContainer.innerHTML = ''; // Clear previous results
        spinner.style.display = 'block';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/budgets/api/get-smart-analysis/');
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get analysis.');
            }
            
            renderAnalysis(data.analysis_results);

        } catch (error) {
            resultsContainer.innerHTML = `<p class="error-message">${error.message}</p>`;
        } finally {
            spinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });

    function renderAnalysis(analysis) {
        if (!analysis || analysis.length === 0) {
            resultsContainer.innerHTML = '<p>No spending data was found to analyze.</p>';
            return;
        }

        analysis.forEach(category => {
            const card = document.createElement('div');
            card.className = 'category-card';

            const header = document.createElement('div');
            header.className = 'category-card-header';
            header.innerHTML = `
                <div class="category-info">
                    <i class="${category.icon} category-icon"></i>
                    <span class="category-name">${category.category_name}</span>
                </div>
                <span class="category-total">₹${category.total_spend.toFixed(2)}</span>
            `;

            const details = document.createElement('div');
            details.className = 'category-details';
            
            category.breakdown.forEach(item => {
                const breakdownItem = document.createElement('div');
                breakdownItem.className = 'breakdown-item';
                breakdownItem.innerHTML = `
                    <span>${item.name} (${item.transaction_count})</span>
                    <strong>₹${item.amount.toFixed(2)}</strong>
                `;
                details.appendChild(breakdownItem);
            });

            header.addEventListener('click', () => {
                details.classList.toggle('show');
            });
            
            card.appendChild(header);
            card.appendChild(details);
            resultsContainer.appendChild(card);
        });
    }
});