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
        // console.error("Error parsing processed categories JSON:", error);
        processedCategories = [];
    }

    // Debug: Log available dropdown options
    if (categorySelect) {
        // console.log("Available dropdown options:");
        for (let option of categorySelect.options) {
            // console.log(`Value: "${option.value}", Text: "${option.textContent}"`);
        }
    }

    // Global function to be called from HTML for editing
    window.editBudget = function(categoryName, budgetAmount, period = 'monthly') {
        if (categorySelect && budgetAmountInput && periodSelect) {
            // console.log('Trying to set category to:', categoryName);
            
            let optionFound = false;
            
            // Try case-insensitive value match first (this worked for you)
            for (let option of categorySelect.options) {
                if (option.value.toLowerCase() === categoryName.toLowerCase()) {
                    categorySelect.value = option.value;
                    optionFound = true;
                    // console.log('Found by case-insensitive value match');
                    break;
                }
            }
            
            if (!optionFound) {
                // console.warn('Category not found in dropdown:', categoryName);
            }
            
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

    // FIXED: Function to update current progress display
    function updateCurrentProgress() {
        const selectedCategory = categorySelect.value;
        
        if (!selectedCategory || !currentProgressDiv) {
            if (currentProgressDiv) currentProgressDiv.style.display = "none";
            return;
        }

        // console.log('Looking for category data for:', selectedCategory);
        // console.log('Available processed categories:', processedCategories);

        // Try different approaches to find the category data
        let categoryData = null;

        // 1. Try exact match with name field
        categoryData = processedCategories.find(cat => cat.name === selectedCategory);
        
        // 2. If not found, try case-insensitive match with name
        if (!categoryData) {
            categoryData = processedCategories.find(cat => 
                cat.name && cat.name.toLowerCase() === selectedCategory.toLowerCase()
            );
        }
        
        // 3. Try to match with display_name field
        if (!categoryData) {
            categoryData = processedCategories.find(cat => 
                cat.display_name && cat.display_name.toLowerCase() === selectedCategory.toLowerCase()
            );
        }
        
        // 4. Try partial matching (in case of slight differences)
        if (!categoryData) {
            categoryData = processedCategories.find(cat => {
                const catName = (cat.name || '').toLowerCase();
                const catDisplay = (cat.display_name || '').toLowerCase();
                const selected = selectedCategory.toLowerCase();
                
                return catName.includes(selected) || 
                       selected.includes(catName) ||
                       catDisplay.includes(selected) || 
                       selected.includes(catDisplay);
            });
        }

        // console.log('Found category data:', categoryData);

        if (categoryData) {
            // Update progress display with existing data
            const spentAmount = parseFloat(categoryData.spent_amount || 0);
            const budgetAmount = parseFloat(categoryData.budget_amount || 0);
            const progressPercentage = parseFloat(categoryData.progress_percentage || 0);
            
            miniSpentSpan.textContent = `₹${spentAmount.toFixed(2)}`;
            miniBudgetSpan.textContent = `₹${budgetAmount.toFixed(2)}`;
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
            // console.log('Progress updated successfully');
        } else {
            // No budget set for this category, show default values
            // console.log('No category data found, showing defaults');
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
            if (e.target.classList.contains('fa-trash') || 
                e.target.closest('.delete-btn')) {
                
                const deleteBtn = e.target.closest(".delete-btn");
                
                if (!deleteBtn) {
                    // console.error('Delete button not found');
                    return;
                }

                const budgetId = deleteBtn.dataset.id;
                const budgetCard = deleteBtn.closest(".budget-card");
                
                if (!budgetCard) {
                    // console.error('Budget card not found');
                    return;
                }
                
                const categoryNameElement = budgetCard.querySelector(".category-info h3");
                const categoryName = categoryNameElement ? categoryNameElement.textContent : 'this item';

                if (!budgetId) {
                    // console.error("Budget ID not found");
                    alert("Error: Budget ID not found");
                    return;
                }

                if (confirm(`Are you sure you want to delete the budget for "${categoryName}"?`)) {
                    deleteBtn.disabled = true;
                    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

                    try {
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
                            budgetCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                            budgetCard.style.opacity = '0';
                            budgetCard.style.transform = 'scale(0.95)';
                            
                            setTimeout(() => {
                                budgetCard.remove();
                                processedCategories = processedCategories.filter(cat => cat.id !== parseInt(budgetId));
                                
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

                            showNotification(data.message || "Budget deleted successfully", "success");
                            
                        } else {
                            throw new Error(data.error || "Failed to delete budget");
                        }
                    } catch (error) {
                        // console.error("Error deleting budget:", error);
                        alert(`Error: ${error.message}`);
                        
                        deleteBtn.disabled = false;
                        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    }
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

    // Utility function to show notifications
    function showNotification(message, type = 'info') {
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
