import { getCookie } from '/static/core/js/help.js';
const csrftoken = getCookie('csrftoken');
let itemCount = 5;
let currentPage = 1;

const sortByEl = document.getElementById("sort-by");
const sortOrderEl = document.getElementById("sort-order");
const categoryFilterEl = document.getElementById("category-filter");

async function fetchAndDisplayTransactions(append = false) {
    try {
        const sortBy = sortByEl.value;
        const sortOrder = sortOrderEl.value;
        const category = categoryFilterEl.value;

        let url = `/transactions/get_transactions/?itemCount=${itemCount}&sortBy=${sortBy}&sortOrder=${sortOrder}&category=${category}&page=${currentPage}`;

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
            tr.dataset.id = transaction.id;

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

        if (loadMoreButton) {
            loadMoreButton.style.display = transactions.length < itemCount ? "none" : "block";
        }
    } catch (error) {
        alert(error.message);
    }
}

function reloadTransactions() {
    currentPage = 1;
    fetchAndDisplayTransactions(false);
}

document.addEventListener("DOMContentLoaded", function () {
    fetchAndDisplayTransactions();

    sortByEl.addEventListener("change", reloadTransactions);
    sortOrderEl.addEventListener("change", reloadTransactions);
    categoryFilterEl.addEventListener("change", reloadTransactions);

    document.addEventListener("click", async (e) => {
        if (e.target.id === "LoadMore") {
            currentPage++;
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
                        reloadTransactions();
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