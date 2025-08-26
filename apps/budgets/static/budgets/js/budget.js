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

    // Global function to be called from HTML for editing
    window.editBudget = function(categoryName, budgetAmount) {
        categorySelect.value = categoryName;
        budgetAmountInput.value = budgetAmount;
        // Assuming period is monthly for now, or you'd need to pass it
        periodSelect.value = "monthly"; 
        updateCurrentProgress(); // Update progress for the selected category
    };

    // Function to reset the form
    resetFormBtn.addEventListener("click", function() {
        budgetForm.reset();
        currentProgressDiv.style.display = "none"; // Hide progress when form is reset
    });

    // Function to update current progress display based on selected category
    async function updateCurrentProgress() {
        const selectedCategory = categorySelect.value;
        if (selectedCategory) {
            // Assuming `processed_categories` is available globally from Django context
            // Or, you would fetch it here if not available
            const processedCategories = JSON.parse(document.getElementById('processed_categories_json').textContent);
            const categoryData = processedCategories.find(cat => cat.name === selectedCategory);

            if (categoryData) {
                miniSpentSpan.textContent = `₹${categoryData.spent_amount.toFixed(2)}`;
                miniBudgetSpan.textContent = `₹${categoryData.budget_amount.toFixed(2)}`;
                miniProgressFill.style.width = `${categoryData.progress_percentage}%`;
                miniPercentageSpan.textContent = `${categoryData.progress_percentage}% used`;
                currentProgressDiv.style.display = "block";
            } else {
                // If no budget set for this category, show default or hide
                miniSpentSpan.textContent = `₹0.00`;
                miniBudgetSpan.textContent = `₹0.00`;
                miniProgressFill.style.width = `0%`;
                miniPercentageSpan.textContent = `0% used`;
                currentProgressDiv.style.display = "block"; // Still show, but with zeros
            }
        } else {
            currentProgressDiv.style.display = "none";
        }
    }

    // Event listener for category selection change
    categorySelect.addEventListener("change", updateCurrentProgress);

    // Initial update in case a category is pre-selected (e.g., after form submission redirect)
    updateCurrentProgress();
});

// The original fetchBudgets and checkBudget are not directly used for display on this page anymore
// but might be used elsewhere or for future enhancements.
// Keeping them here for now, but they are not part of the DOMContentLoaded logic above.
let budgets = {}; // This global `budgets` might be redundant if data is passed via Django context

async function fetchBudgets() {
    try {
        const response = await fetch("/budgets/get_budgets/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        });
        const data = await response.json();
        if (response.ok) {
            budgets = data.budgets;
        } else {
            throw new Error(data.error || "Failed to fetch budgets");
        }
    } catch (error) {
        console.error("Error fetching budgets for checkBudget:", error);
    }
}

function checkBudget(category, amount) {
    // This function is likely used in add_transaction.js, not here.
    // It would need to fetch the latest budget data if not already available.
    if (budgets[category] && amount > budgets[category]) {
        alert(`Warning: This transaction exceeds the budget for ${category}.`);
    }
}

// Call fetchBudgets if checkBudget is still intended to be used on this page
// fetchBudgets();