import { getCookie } from './help.js';
const csrftoken = getCookie('csrftoken');
let itemCount = 10;

async function fetchAndDisplayIncomes() {
    try {
        const response = await fetch(`/get_incomes/?itemCount=${itemCount}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const incomes = data.incomes || [];
        const tbody = document.querySelector(".incomeTable tbody"); // Ensure correct ID

        if (!tbody) {
            console.error("Table body not foualnd! Make sure #incomeTableBody exists.");
            return;
        }

        tbody.innerHTML = ""; // Clear existing rows

        if (incomes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No income records found.</td></tr>`;
            return;
        }
        const fragment = document.createDocumentFragment();

        incomes.forEach(income => {
            const transaction = income.transaction;
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <tr data-id="${income.id}">
                <td>${transaction.name || "No Name"}</td>
                <td>${transaction.source || "No Source"}</td>
                <td>₹${transaction.amount.toFixed(2) || 0}</td>
                <td>${new Date(transaction.date).toLocaleDateString()}</td>
                <td class="status-${transaction.status.toLowerCase()}">${transaction.status}</td>
                <td>
                    <button class="delete-btn" data-id="${income.id}">Delete</button>
                </td>
                <td>
            <button class="edit-btn" data-id="${income.id}">Edit</button>
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
document.addEventListener("DOMContentLoaded", fetchAndDisplayIncomes);

document.addEventListener("DOMContentLoaded", function () {
    const dropdownButtons = document.querySelectorAll(".drop-btn");
        dropdownButtons.forEach(button => {
            button.addEventListener("click", function () {
                const dropdownContent = this.nextElementSibling;
                const icon = this.querySelector(".dropdown-icon");
    
                dropdownContent.classList.toggle("active");
    
                if (dropdownContent.classList.contains("active")) {
                    dropdownContent.style.display = "block";
                    icon.classList.remove("fa-angle-right");
                    icon.classList.add("fa-angle-down");
                } else {
                    dropdownContent.style.display = "none";
                    icon.classList.remove("fa-angle-down");
                    icon.classList.add("fa-angle-right");
                }
            });
    });
});

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

document.addEventListener("click", async (e) => {
    if (e.target.id.includes("LoadMore")) {
        itemCount+=5;
        await fetchAndDisplayIncomes();
    }
});

