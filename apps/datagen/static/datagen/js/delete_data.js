import { getCookie } from '/static/core/js/help.js';

document.addEventListener('DOMContentLoaded', () => {
    const deleteBtn = document.getElementById('delete-btn');
    const statusMessage = document.getElementById('status-message');

    deleteBtn.addEventListener('click', async () => {
        // Double confirmation to prevent accidental deletion
        if (!confirm('Are you absolutely sure? This action cannot be undone.')) {
            return;
        }

        statusMessage.style.display = 'none';
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting...';

        try {
            const response = await fetch('/datagen/api/delete-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
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
            // Keep the button disabled after a successful deletion to prevent re-clicks
            if (statusMessage.classList.contains('success')) {
                deleteBtn.textContent = 'Data Deleted';
            } else {
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Yes, I understand. Delete all my data.';
            }
        }
    });
});