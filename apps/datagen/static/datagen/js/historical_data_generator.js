import { getCookie } from '/static/core/js/help.js';

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const statusMessage = document.getElementById('status-message');

    generateBtn.addEventListener('click', async () => {
        const constraints = {
            num_transactions: document.getElementById('num-transactions').value,
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
            district: document.getElementById('district').value,
            min_amount: document.getElementById('min-amount').value,
            max_amount: document.getElementById('max-amount').value,
        };

        if (!constraints.start_date || !constraints.end_date) {
            alert('Please select a start and end date.');
            return;
        }

        statusMessage.style.display = 'none';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        try {
            const response = await fetch('/datagen/api/generate-historical-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(constraints),
            });

            const data = await response.json();
            
            statusMessage.textContent = data.message || data.error;
            statusMessage.className = response.ok ? 'status-message success' : 'status-message error';
            statusMessage.style.display = 'block';

        } catch (error) {
            statusMessage.textContent = 'A network error occurred.';
            statusMessage.className = 'status-message error';
            statusMessage.style.display = 'block';
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Historical Data';
        }
    });
});