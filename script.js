let screenerData = [];

const tableBody = document.querySelector("#screener-table tbody");
const filterSelect = document.getElementById("filter");

// Load JSON data
fetch("results.json")
    .then(response => response.json())
    .then(data => {
        screenerData = data;
        renderTable("ALL");
    })
    .catch(error => {
        console.error("Error loading data:", error);
    });

// Render table based on filter
function renderTable(filter) {
    tableBody.innerHTML = "";

    screenerData.forEach(item => {
        if (filter !== "ALL" && item.status !== filter) {
            return;
        }

        const row = document.createElement("tr");

        if (item.status === "HIGH") {
            row.classList.add("high");
        } else if (item.status === "LOW") {
            row.classList.add("low");
        }

        row.innerHTML = `
            <td>${item.symbol}</td>
            <td>${item.monthly.high} / ${item.monthly.low}</td>
            <td>${item.weekly.high} / ${item.weekly.low}</td>
            <td>${item.daily.high} / ${item.daily.low}</td>
            <td>${item.cmp}</td>
        `;

        tableBody.appendChild(row);
    });
}

// Filter change event
filterSelect.addEventListener("change", () => {
    renderTable(filterSelect.value);
});

