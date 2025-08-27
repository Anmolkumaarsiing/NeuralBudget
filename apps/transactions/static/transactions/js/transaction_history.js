import { getCookie } from '/static/core/js/help.js';
const csrftoken = getCookie('csrftoken');
let itemCount = 5;
let lastDocId = null;

async function fetchAndDisplayTransactions(append = false) {
    try {
        let url = `/transactions/get_transactions/?itemCount=${itemCount}`;
        if (lastDocId && append) { // Only add lastDocId if appending
            url += `&lastDocId=${lastDocId}`;
        }

        const response = await fetch(url, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const transactions = data.transactions || [];
        const tbody = document.querySelector(".incomeTable tbody");
        const loadMoreButton = document.getElementById("LoadMore");

        if (!tbody) {
            console.error("Table body not found!");
            return;
        }

        if (!append) {
            tbody.innerHTML = "";
        }

        if (transactions.length === 0 && !append) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center;">No transaction records found.</td></tr>`;
            if (loadMoreButton) loadMoreButton.style.display = "none";
            return;
        }

        transactions.forEach(transaction => {
            const tr = document.createElement("tr");
            tr.dataset.id = transaction.id; // Set data-id on the correct tr

            const statusClass = (transaction.status || 'pending').toLowerCase().replace(/\s+/g, '-');

            tr.innerHTML = `
                <td data-label="Name">${transaction.name || transaction.source || "N/A"}</td>
                <td data-label="Category">${transaction.category || "Income"}</td>
                <td data-label="Amount">₹${(transaction.amount || 0).toFixed(2)}</td>
                <td data-label="Date">${new Date(transaction.date).toLocaleDateString()}</td>
                <td data-label="Status">
                    <span class="status-badge status-${statusClass}">${transaction.status || "Pending"}</span>
                </td>
                <td data-label="Type">${transaction.type}</td>
                <td data-label="Delete">
                    <button class="delete-btn" data-id="${transaction.id}">Delete</button>
                </td>
                <td data-label="Edit">
                    <button class="edit-btn" data-id="${transaction.id}">Edit</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        if (transactions.length > 0) {
            lastDocId = transactions[transactions.length - 1].id;
        }

        if (loadMoreButton) {
            loadMoreButton.style.display = transactions.length < itemCount ? "none" : "block";
        }
    } catch (error) {
        alert(error.message);
    }
}

function reloadTransactions() {
    lastDocId = null; // Reset pagination
    fetchAndDisplayTransactions(false); // Call with append=false to clear the table
}

// --- Combined Event Listeners for cleaner code ---
document.addEventListener("DOMContentLoaded", function () {
    // Initial load
    fetchAndDisplayTransactions();

    // Listener for sidebar dropdowns
    document.querySelectorAll(".drop-btn").forEach(button => {
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

    // Listener for clicks on the whole page (Load More, Delete)
    document.addEventListener("click", async (e) => {
        if (e.target.id === "LoadMore") {
            await fetchAndDisplayTransactions(true);
        }

        if (e.target.classList.contains("delete-btn")) {
            const transactionId = e.target.getAttribute("data-id");
            const transactionType = e.target.closest('tr').querySelector('td:nth-child(6)').textContent;
            const collectionName = transactionType.trim() === 'Income' ? 'incomes' : 'expenses';

            if (confirm("Are you sure you want to delete this transaction?")) {
                try {
                    const response = await fetch(`/transactions/delete_transaction/?transaction_id=${transactionId}&collection=${collectionName}`, {
                        method: "DELETE",
                        headers: { "X-CSRFToken": csrftoken },
                    });
                    const data = await response.json();
                    if (response.ok) {
                        alert("Transaction deleted successfully!");
                        reloadTransactions();  // Remove row by reloading
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
});