document.getElementById("darkModeToggle").addEventListener("change", function () {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
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

// Dummy data for dashboard cards
document.getElementById("totalExpenses").innerText = "₹1,250.00";
document.getElementById("savings").innerText = "₹3,400.00";
document.getElementById("budgetLeft").innerText = "₹750.00";

// Dummy data for transactions with categories
const transactions = [
    { name: "Groceries", amount: "₹50.00", type: "Spent" },
    { name: "Salary", amount: "₹2,000.00", type: "Received" },
    { name: "Netflix", amount: "₹15.00", type: "Bill Payment" }
];

const transactionList = document.getElementById("transactionList");
transactionList.innerHTML = transactions
    .map(t => `
        <li>
            <span class="txn-name">${t.name}:</span> 
            <span class="txn-amount">${t.amount}</span> 
            <span class="txn-type">${t.type}</span>
        </li>
    `)
    .join("");

    // document.addEventListener("DOMContentLoaded", function () {
    //     const ctx = document.getElementById("expenseChart").getContext("2d");
    //     if (!ctx) {
    //         console.error("Canvas element not found!");
    //         return;
    //     }
    
    //     new Chart(ctx, {
    //         type: "doughnut", 
    //         data: {
    //             labels: ["Groceries", "Entertainment", "Utilities", "Rent", "Shopping"],
    //             datasets: [{
    //                 label: "Expense Distribution",
    //                 data: [200, 150, 100, 500, 250], 
    //                 backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9C27B0"],
    //                 borderWidth: 1
    //             }]
    //         },
    //         options: {
    //             responsive: true,
    //             maintainAspectRatio: false,
    //             plugins: {
    //                 legend: {
    //                     position: "bottom"
    //                 }
    //             }
    //         }
    //     });
    // });