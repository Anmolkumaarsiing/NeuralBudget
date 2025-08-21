import { getCookie } from '/static/core/js/help.js';

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const numInput = document.getElementById('num-transactions');
    const statusMessage = document.getElementById('status-message');

    generateBtn.addEventListener('click', async () => {
        const numTransactions = numInput.value;
        statusMessage.style.display = 'none';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        try {
            const response = await fetch('/datagen/api/generate-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ num_transactions: numTransactions }),
            });

            const data = await response.json();
            
            statusMessage.textContent = data.message || data.error;
            statusMessage.className = response.ok ? 'status-message success' : 'status-message error';
            statusMessage.style.display = 'block';

        } catch (error) {
            statusMessage.textContent = 'A network error occurred. Please try again.';
            statusMessage.className = 'status-message error';
            statusMessage.style.display = 'block';
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Data';
        }
    });
});