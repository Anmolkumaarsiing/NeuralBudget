// budgets/static/budgets/js/savings_goals.js

document.addEventListener('DOMContentLoaded', () => {

    // --- Modal Control ---
    const modal = document.getElementById('goal-modal');
    const createGoalBtn = document.getElementById('create-goal-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');

    if (createGoalBtn) {
        createGoalBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Close modal if user clicks on the overlay
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // --- Confetti Animation ---
    // Example: Trigger confetti when a "complete" button is clicked
    // In a real app, you would call this after a goal is marked as complete
    const completeButton = document.querySelector('.goal-card.completed'); // Example selector
    if(completeButton) {
        // We'll add a click listener to the completed card for demo purposes
        completeButton.addEventListener('click', () => {
            fireConfetti();
        });
    }

});


// --- Simple Confetti Function ---
function fireConfetti() {
    const confettiCount = 100;
    const confettiContainer = document.body;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.animationDuration = Math.random() * 3 + 2 + 's';
        confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
        
        confettiContainer.appendChild(confetti);
        
        confetti.addEventListener('animationend', () => {
            confetti.remove();
        });
    }
}

// Add this CSS to your main stylesheet (e.g., dashboard.css) for the confetti
/*

*/