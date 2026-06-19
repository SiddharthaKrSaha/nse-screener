let screenerData = [];

/* ===== Visitor Counter (6-digit, browser-based) ===== */
let visits = localStorage.getItem("visits") || 0;
visits++;
localStorage.setItem("visits", visits);

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("visitorCount").textContent =
    String(visits).padStart(6, "0");
});


/* ===== Fetch Data ===== */
fetch("results.json")
  .then(res => res.json())
  .then(data => {
    screenerData = data;
    renderTable("ALL");
  });


/* ===== Main Filter Change Event ===== */
document.getElementById("filter").addEventListener("change", e => {
  renderTable(e.target.value);
});


/* ===== CMP Sort Change Event ===== */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("cmpSort").addEventListener("change", () => {
    renderTable(document.getElementById("filter").value);
  });
});


/* ===== Render Table ===== */
function renderTable(filter) {
  const tbody = document.querySelector("#screener-table tbody");
  tbody.innerHTML = "";

  let dataToRender = [...screenerData];

  /* ===== CMP Sorting ===== */
  const cmpSort = document.getElementById("cmpSort").value;

  if (cmpSort === "ASC") {
    dataToRender.sort((a, b) => a.cmp - b.cmp);
  }

  dataToRender.forEach(item => {

    if (
      item.monthly === "SIDEWAYS" ||
      item.weekly === "SIDEWAYS" ||
      item.daily === "SIDEWAYS"
    ) return;

    const isUp =
      item.monthly === "UP" &&
      item.weekly === "UP" &&
      item.daily === "UP";

    const isDown =
      item.monthly === "DOWN" &&
      item.weekly === "DOWN" &&
      item.daily === "DOWN";

    if (
      (filter === "GREEN" && !isUp) ||
      (filter === "RED" && !isDown)
    ) return;

    const trendClass = isUp ? "trend-up" : "trend-down";

    const row = document.createElement("tr");

    row.innerHTML = `
      <td class="${trendClass}">${item.symbol}</td>
      <td class="cmp">${item.cmp}</td>
      <td class="${trendClass}">${item.trend}</td>
    `;

    tbody.appendChild(row);
  });

  /* ===== Row Count Update ===== */
  document.getElementById("rowCount").textContent =
    document.querySelectorAll("#screener-table tbody tr").length;
}
