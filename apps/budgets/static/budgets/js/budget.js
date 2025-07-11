import { getCookie } from "/static/core/js/help.js";

let budgets = {};

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
        console.error("Error:", error);
    }
}

function checkBudget(category, amount) {
    if (budgets[category] && amount > budgets[category]) {
        alert(`Warning: This transaction exceeds the budget for ${category}.`);
    }
}

// Fetch budgets on page load
fetchBudgets();
