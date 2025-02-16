

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
            tbody.innerHTML = `<tr><td colspan="4">No income records found.</td></tr>`;
            return;
        }
        const amount = parseFloat(incomes.amount);
        console.log(amount);

        incomes.forEach(income => {
            const transaction = income.transaction; // Extract transaction object
            if (!transaction) return;
            const amount = parseFloat(transaction.amount) || 0;

            const row = `
                <tr>
                    <td>${transaction.name}</td>
                    <td>${transaction.category}</td>
                    <td>₹${amount.toFixed(2)}</td>
                    <td>${new Date(transaction.date).toLocaleDateString()}</td>
                    <td class="status-${transaction.status.toLowerCase()}">${transaction.status}</td>
                </tr>
            `;
            tbody.insertAdjacentHTML("beforeend", row);
        });
        

    } catch (error) {
        alert(error.message);
    }
}

// Ensure script runs after page is fully loaded
document.addEventListener("DOMContentLoaded", fetchAndDisplayIncomes);
