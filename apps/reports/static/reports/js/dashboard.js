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

    const ctx = document.getElementById("expenseChart").getContext("2d");
    if (ctx && typeof expenseChartData !== 'undefined') {
        new Chart(ctx, {
            type: "doughnut", 
            data: {
                labels: expenseChartData.labels,
                datasets: [{
                    label: "Expense Distribution",
                    data: expenseChartData.data,
                    backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9C27B0", "#FF9F40", "#4BC0C0", "#9966FF"], // Add more colors if needed
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }
});