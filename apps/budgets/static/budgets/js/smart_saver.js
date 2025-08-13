// in apps/budgets/static/budgets/js/smart_saver.js

/**
 * Helper function to get the CSRF token from the browser's cookies.
 * This is the official function provided in the Django documentation.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('smart-saver-form');
    const planDisplay = document.getElementById('plan-display');
    const loadingSpinner = document.getElementById('loading-spinner');
    let savingsChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        planDisplay.style.display = 'none';
        loadingSpinner.style.display = 'block';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/budgets/smart-saver/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // This will now work correctly
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                // Try to get a more specific error message from the backend if available
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || 'Something went wrong. SAVI is taking a short nap!';
                throw new Error(errorMessage);
            }

            const plan = await response.json();
            renderPlan(plan);

        } catch (error) {
            alert(error.message);
        } finally {
            loadingSpinner.style.display = 'none';
        }
    });

    function renderPlan(plan) {
    document.getElementById('plan-title').textContent = plan.title;
    document.getElementById('plan-summary').textContent = plan.summary;

    const stepsContainer = document.getElementById('plan-steps');
    stepsContainer.innerHTML = ''; // Clear previous steps

    plan.plan_steps.forEach(step => {
        const stepCard = document.createElement('div');
        stepCard.className = 'step-card';
        // --- THIS HTML STRUCTURE IS UPDATED ---
        stepCard.innerHTML = `
            <div class="step-header">
                <div class="step-title-group">
                    <i class="${step.icon} step-icon"></i>
                    <h4 class="step-title">${step.title}</h4>
                </div>
                <span class="step-savings">+ ₹${step.potential_savings}/month</span>
            </div>
            <p>${step.description}</p>
        `;
        stepsContainer.appendChild(stepCard);
    });

    const ctx = document.getElementById('savings-chart').getContext('2d');
    if (savingsChart) {
        savingsChart.destroy(); // Destroy old chart before creating new one
    }
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: plan.chart_data.labels,
            datasets: [{
                label: 'Projected Savings Growth',
                data: plan.chart_data.values,
                backgroundColor: 'rgba(36, 167, 145, 0.2)', // Use your theme color
                borderColor: 'rgba(36, 167, 145, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    planDisplay.style.display = 'block';
}
});