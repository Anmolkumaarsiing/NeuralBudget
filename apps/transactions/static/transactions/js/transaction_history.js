import { getCookie } from '/static/core/js/help.js';
const csrftoken = getCookie('csrftoken');
let itemCount = 10; // Initial batch size
let lastDocId = null; // To store the ID of the last document fetched

async function fetchAndDisplayTransactions(append = false) {
    try {
        let url = `/transactions/get_transactions/?itemCount=${itemCount}`;
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
        const transactions = data.transactions || [];
        const tbody = document.querySelector(".incomeTable tbody");
        const loadMoreButton = document.getElementById("LoadMore");

        if (!tbody) {
            console.error("Table body not found! Make sure .incomeTable tbody exists.");
            return;
        }

        if (!append) {
            tbody.innerHTML = ""; // Clear existing rows only if not appending
        }

        if (transactions.length === 0 && !append) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center;">No transaction records found.</td></tr>`;
            if (loadMoreButton) loadMoreButton.style.display = "none"; // Hide if no records at all
            return;
        }

        const fragment = document.createDocumentFragment();

        transactions.forEach(transaction => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <tr data-id="${transaction.id}">
                <td>${transaction.name || transaction.source || "No Name"}</td>
                <td>${transaction.category || "-"}</td>
                <td>₹${transaction.amount.toFixed(2) || 0}</td>
                <td>${new Date(transaction.date).toLocaleDateString()}</td>
                <td class="status-${transaction.status.toLowerCase()}">${transaction.status}</td>
                <td>${transaction.type}</td>
                <td>
                    <button class="delete-btn" data-id="${transaction.id}">Delete</button>
                </td>
                <td>
            <button class="edit-btn" data-id="${transaction.id}">Edit</button>
        </td>
            </tr>
            `;
            fragment.appendChild(tr);
        });
        tbody.appendChild(fragment);

        // Update lastDocId with the ID of the last fetched transaction
        if (transactions.length > 0) {
            lastDocId = transactions[transactions.length - 1].id;
        }

        // Control Load More button visibility
        if (loadMoreButton) {
            if (transactions.length < itemCount) { // If fewer records than requested, no more to load
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
    fetchAndDisplayTransactions();
});

document.addEventListener("click", async (e) => {
    if (e.target.id === "LoadMore") {
        // itemCount remains the batch size (5)
        await fetchAndDisplayTransactions(true); // Pass true to append
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
        const transactionId = e.target.getAttribute("data-id");
        const transactionType = e.target.closest('tr').querySelector('td:nth-child(6)').textContent; // Get the type (Income/Expense)
        const collectionName = transactionType === 'Income' ? 'incomes' : 'transactions';

        console.log(`Attempting to delete ID: ${transactionId} from collection: ${collectionName}`);

        if (confirm("Are you sure you want to delete this transaction?")) {
            try {
                const response = await fetch(`/transactions/delete_transaction/?transaction_id=${transactionId}&collection=${collectionName}`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": csrftoken,
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

