// This file is the same as the one from the "Smart Categorization" feature
// It handles the button click and renders the results.
document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const spinner = document.getElementById('loading-spinner');
    const resultsContainer = document.getElementById('results-container');

    if (!analyzeBtn) return;

    analyzeBtn.addEventListener('click', async () => {
        spinner.style.display = 'block';
        analyzeBtn.disabled = true;
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch('/insights/api/get-smart-analysis/');
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            renderAnalysis(data.analysis_results);
        } catch (error) {
            resultsContainer.innerHTML = `<p style="color: red;">${error.message}</p>`;
        } finally {
            spinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });

    function renderAnalysis(analysis) {
        // ... (The renderAnalysis function is the same as before) ...
    }
});