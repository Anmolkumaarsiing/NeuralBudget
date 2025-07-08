import { getCookie } from './help.js';
const csrftoken = getCookie('csrftoken');
let itemCount = 5; // Initial batch size
let lastDocId = null; // To store the ID of the last document fetched

async function fetchAndDisplayIncomes(append = false) {
    try {
        let url = `/get_incomes/?itemCount=${itemCount}`;
        if (lastDocId) {
            url += `&lastDocId=${lastDocId}`;
        }

        const response = await fetch(url, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const incomes = data.incomes || [];
        const tbody = document.querySelector(".incomeTable tbody");
        const loadMoreButton = document.getElementById("LoadMore");

        if (!tbody) {
            console.error("Table body not found! Make sure .incomeTable tbody exists.");
            return;
        }

        if (!append) {
            tbody.innerHTML = ""; // Clear existing rows only if not appending
        }

        if (incomes.length === 0 && !append) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center;">No income records found.</td></tr>`;
            if (loadMoreButton) loadMoreButton.style.display = "none"; // Hide if no records at all
            return;
        }

        const fragment = document.createDocumentFragment();

        incomes.forEach(income => {
            const transaction = income.transaction;
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <tr data-id="${income.id}">
                <td>${transaction.name || "No Name"}</td>
                <td>${transaction.category || "No Source"}</td>
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
        tbody.appendChild(fragment);

        // Update lastDocId with the ID of the last fetched income
        if (incomes.length > 0) {
            lastDocId = incomes[incomes.length - 1].id;
        }

        // Control Load More button visibility
        if (loadMoreButton) {
            if (incomes.length < itemCount) { // If fewer records than requested, no more to load
                loadMoreButton.style.display = "none";
            } else {
                loadMoreButton.style.display = "block"; // Ensure it's visible if there might be more
            }
        }
    } catch (error) {
        alert(error.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Reset lastDocId and itemCount for initial load
    lastDocId = null;
    itemCount = 5; // Initial batch size
    fetchAndDisplayIncomes();
});

document.addEventListener("click", async (e) => {
    if (e.target.id === "LoadMore") {
        // itemCount remains the batch size (5)
        await fetchAndDisplayIncomes(true); // Pass true to append
    }
});


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

