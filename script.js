let screenerData = [];

const tableBody = document.querySelector("#screener-table tbody");

// Load JSON data
fetch("results.json")
    .then(response => response.json())
    .then(data => {
        screenerData = data;
        renderTable();
    })
    .catch(error => {
        console.error("Error loading data:", error);
    });

// Render table
function renderTable() {
    tableBody.innerHTML = "";

    screenerData.forEach(item => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.symbol}</td>
            <td></td>
            <td></td>
            <td></td>
            <td>${item.cmp}</td>
        `;

        tableBody.appendChild(row);
    });
}
