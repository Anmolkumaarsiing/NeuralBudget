import { getCookie } from './help.js';
const csrftoken = getCookie('csrftoken');

async function fetchAndDisplayIncomes() {
    try {
        const response = await fetch(`/get_incomes/`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const incomes = data.incomes || [];
        const tbody = document.querySelector(".incomeTable tbody"); // Ensure correct ID

        if (!tbody) {
            console.error("Table body not found! Make sure #incomeTableBody exists.");
            return;
        }

        tbody.innerHTML = ""; // Clear existing rows

        if (incomes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No income records found.</td></tr>`;
            return;
        }
        const fragment = document.createDocumentFragment();

        incomes.forEach(income => {
            const transaction = income;
            console.log(transaction);

            const tr = document.createElement("tr");
            tr.innerHTML = `
            <tr data-id="${income.id}">
                <td>${transaction.name}</td>
                <td>${transaction.source.toString()}</td>
                <td>₹${transaction.amount.toFixed(2) || 0}</td>
                <td>${new Date(transaction.date).toLocaleDateString()}</td>
                <td class="status-${transaction.status.toLowerCase()}">${transaction.status}</td>
                <td>
                    <button class="delete-btn" data-id="${income.id}">Delete</button>
                </td>
            </tr>
            `;
            fragment.appendChild(tr);
        });
        tbody.appendChild(fragment); // Append all at once
    } catch (error) {
        alert(error.message);
    }
}

// Ensure script runs after page is fully loaded
document.addEventListener("DOMContentLoaded", fetchAndDisplayIncomes);

document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("delete-btn")) {
        const incomeId = e.target.getAttribute("data-id");
        console.log(incomeId);
        if (confirm("Are you sure you want to delete this transaction?")) {
            try {
                const response = await fetch(`/delete_income/?income_id=${incomeId}`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken":  csrftoken,
                    },
                });

                const data = await response.json();
                if (response.ok) {
                    alert("Transaction deleted successfully!");
                    window.location.reload();
                } else {
                    throw new Error(data.error || "Failed to delete transaction");
                }
            } catch (error) {
                console.error("Error deleting transaction:", error);
                alert(error.message);
            }
        }
    }
});
