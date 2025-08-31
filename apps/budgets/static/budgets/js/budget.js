import { getCookie } from "/static/core/js/help.js";

document.addEventListener("DOMContentLoaded", function() {
    const budgetForm = document.getElementById("budgetForm");
    const categorySelect = document.getElementById("category");
    const budgetAmountInput = document.getElementById("budget-amount");
    const periodSelect = document.getElementById("period");
    const resetFormBtn = document.getElementById("resetForm");
    const currentProgressDiv = document.getElementById("currentProgress");
    const miniSpentSpan = document.getElementById("miniSpent");
    const miniBudgetSpan = document.getElementById("miniBudget");
    const miniProgressFill = document.getElementById("miniProgressFill");
    const miniPercentageSpan = document.getElementById("miniPercentage");
    const budgetGrid = document.querySelector(".budget-grid");

    // Cache processed categories data on page load
    let processedCategories = [];
    try {
        const categoriesElement = document.getElementById('processed_categories_json');
        if (categoriesElement) {
            processedCategories = JSON.parse(categoriesElement.textContent);
        }
    } catch (error) {
        console.error("Error parsing processed categories JSON:", error);
        processedCategories = [];
    }

    // Global function to be called from HTML for editing
    window.editBudget = function(categoryName, budgetAmount, period = 'monthly') {
        if (categorySelect && budgetAmountInput && periodSelect) {
            categorySelect.value = categoryName;
            budgetAmountInput.value = budgetAmount;
            periodSelect.value = period;
            updateCurrentProgress();
            
            // Scroll to form for better UX
            budgetForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    // Function to reset the form
    if (resetFormBtn) {
        resetFormBtn.addEventListener("click", function() {
            budgetForm.reset();
            currentProgressDiv.style.display = "none";
        });
    }

    // Function to update current progress display based on selected category
    function updateCurrentProgress() {
        const selectedCategory = categorySelect.value;
        
        if (!selectedCategory || !currentProgressDiv) {
            if (currentProgressDiv) currentProgressDiv.style.display = "none";
            return;
        }

        const categoryData = processedCategories.find(cat => cat.name === selectedCategory);

        if (categoryData) {
            // Update progress display with existing data
            miniSpentSpan.textContent = `₹${parseFloat(categoryData.spent_amount || 0).toFixed(2)}`;
            miniBudgetSpan.textContent = `₹${parseFloat(categoryData.budget_amount || 0).toFixed(2)}`;
            
            const progressPercentage = parseFloat(categoryData.progress_percentage || 0);
            miniProgressFill.style.width = `${progressPercentage}%`;
            miniPercentageSpan.textContent = `${progressPercentage}% used`;
            
            // Update progress bar color based on percentage
            miniProgressFill.className = 'mini-progress-fill';
            if (progressPercentage <= 50) {
                miniProgressFill.classList.add('green');
            } else if (progressPercentage <= 80) {
                miniProgressFill.classList.add('yellow');
            } else {
                miniProgressFill.classList.add('red');
            }
            
            currentProgressDiv.style.display = "block";
        } else {
            // No budget set for this category, show default values
            miniSpentSpan.textContent = `₹0.00`;
            miniBudgetSpan.textContent = `₹0.00`;
            miniProgressFill.style.width = `0%`;
            miniProgressFill.className = 'mini-progress-fill';
            miniPercentageSpan.textContent = `0% used`;
            currentProgressDiv.style.display = "block";
        }
    }

    // Event listener for category selection change
    if (categorySelect) {
        categorySelect.addEventListener("change", updateCurrentProgress);
    }

    // Event delegation for delete buttons
    if (budgetGrid) {
        budgetGrid.addEventListener("click", async function(e) {
            const deleteBtn = e.target.closest(".delete-btn");
            console.log("clicked", deleteBtn);

            const budgetId = deleteBtn.dataset.id;
            const budgetCard = deleteBtn.closest(".budget-card");
            const categoryName = budgetCard.querySelector(".category-info h3").textContent;

            if (!budgetId) {
                console.error("Budget ID not found");
                alert("Error: Budget ID not found");
                return;
            }

            if (confirm(`Are you sure you want to delete the budget for "${categoryName}"?`)) {
                // Disable button during request
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

                try {
                    console.log("Deleting budget with ID:", budgetId);
                    const response = await fetch("/budgets/delete_budget/", {
                        method: "DELETE",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCookie("csrftoken"),
                        },
                        body: JSON.stringify({ budget_id: budgetId }),
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Remove the card from the DOM with animation
                        budgetCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                        budgetCard.style.opacity = '0';
                        budgetCard.style.transform = 'scale(0.95)';
                        
                        setTimeout(() => {
                            budgetCard.remove();
                            
                            // Update cached data
                            processedCategories = processedCategories.filter(cat => cat.id !== parseInt(budgetId));
                            
                            // Show "no budgets" message if grid is empty
                            const remainingCards = budgetGrid.querySelectorAll('.budget-card');
                            if (remainingCards.length === 0) {
                                budgetGrid.innerHTML = `
                                    <div class="no-budgets">
                                        <i class="fas fa-plus-circle"></i>
                                        <h3>No budgets set yet</h3>
                                        <p>Use the form on the right to create your first budget</p>
                                    </div>
                                `;
                            }
                        }, 300);

                        // Show success message
                        showNotification(data.message || "Budget deleted successfully", "success");
                        
                    } else {
                        throw new Error(data.error || "Failed to delete budget");
                    }
                } catch (error) {
                    console.error("Error deleting budget:", error);
                    alert(`Error: ${error.message}`);
                    
                    // Re-enable button on error
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                }
            }
        });
    }

    // Form submission handling
    if (budgetForm) {
        budgetForm.addEventListener("submit", function(e) {
            const submitBtn = budgetForm.querySelector('.save-btn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            }
        });
    }

    // Utility function to show notifications (optional enhancement)
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Add CSS animations for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Initial update in case a category is pre-selected
 updateCurrentProgress();
});