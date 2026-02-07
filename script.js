let screenerData = [];

fetch("results.json")
  .then(res => res.json())
  .then(data => {
    screenerData = data;
    renderTable("ALL");
  });

document.getElementById("filter").addEventListener("change", e => {
  renderTable(e.target.value);
});

function renderTable(filter) {
  const tbody = document.querySelector("#screener-table tbody");
  tbody.innerHTML = "";

  screenerData.forEach(item => {
    const isUp = item.monthly === "UP" && item.weekly === "UP" && item.daily === "UP";
    const isDown = item.monthly === "DOWN" && item.weekly === "DOWN" && item.daily === "DOWN";

    if (
      filter === "GREEN" && !isUp ||
      filter === "RED" && !isDown
    ) return;

    const trendClass = isUp ? "trend-up" : "trend-down";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="${trendClass}">${item.symbol}</td>
      <td class="cmp">${item.cmp}</td>
      <td class="${trendClass}">${item.monthly}</td>
      <td class="${trendClass}">${item.weekly}</td>
      <td class="${trendClass}">${item.daily}</td>
    `;
    tbody.appendChild(row);
  });
}
