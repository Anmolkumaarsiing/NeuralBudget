document.addEventListener("DOMContentLoaded", function () {
    const insightsBtn = document.getElementById("spending-insights-btn");
    const insightsSection = document.getElementById("spending-insights-section");
    const dashboardSection = document.querySelector(".dashboard");
    const expenseChartCanvas = document.getElementById("expenseChart");

    // Handle "Spending Insights" Button Click
    insightsBtn.addEventListener("click", function () {
        // Hide dashboard
        dashboardSection.style.display = "none";

        // Show Spending Insights Section
        insightsSection.style.display = "block";

        // Check if Chart.js is already initialized
        if (!expenseChartCanvas.dataset.chartLoaded) {
            console.log("📢 Fetching expense data...");  // Debugging log

            fetch("/fetch_expenses/")  // Django API call to get expense data
                .then(response => response.json())
                .then(data => {
                    console.log("✅ Data received from Django:", data);  // Debugging log

                    const labels = [];
                    const values = [];
                    const categoryMap = {};

                    // 🏷️ Group expenses by category
                    data.expenses.forEach(expense => {
                        console.log("🔍 Processing expense:", expense);  // Debugging log

                        const category = expense.category || "Uncategorized"; // Handle missing category
                        const amount = parseFloat(expense.amount) || 0; // Handle invalid amounts

                        if (categoryMap[category]) {
                            categoryMap[category] += amount;
                        } else {
                            categoryMap[category] = amount;
                        }
                    });

                    console.log("📊 Final category-wise data:", categoryMap);  // Debugging log

                    for (const category in categoryMap) {
                        labels.push(category);
                        values.push(categoryMap[category]);
                    }

                    // 🎨 Draw the Chart
                    new Chart(expenseChartCanvas.getContext("2d"), {
                        type: "pie",
                        data: {
                            labels: labels,
                            datasets: [{
                                label: "Expenses by Category",
                                data: values,
                                backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff", "#ff9f40"],
                                borderColor: "#333",
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                }
                            }
                        }
                    });

                    console.log("📈 Chart successfully rendered!");  // Debugging log

                    // ✅ Mark chart as loaded so it doesn't reload on every click
                    expenseChartCanvas.dataset.chartLoaded = "true";
                })
                .catch(error => {
                    console.error("❌ Error fetching expenses:", error);
                });
        }
    });
});
