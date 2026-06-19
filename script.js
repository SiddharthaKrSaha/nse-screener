let screenerData = [];

/* ===== Visitor Counter ===== */
let visits = localStorage.getItem("visits") || 0;
visits++;
localStorage.setItem("visits", visits);

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("visitorCount").textContent =
    String(visits).padStart(6, "0");
});

/* ===== Page Navigation ===== */

document.addEventListener("DOMContentLoaded", () => {

  document.getElementById("page1Btn").addEventListener("click", () => {

    document.getElementById("page1").style.display = "block";
    document.getElementById("page2").style.display = "none";

    document.getElementById("page1Btn").classList.add("active-page");
    document.getElementById("page2Btn").classList.remove("active-page");
  });

  document.getElementById("page2Btn").addEventListener("click", () => {

    document.getElementById("page1").style.display = "none";
    document.getElementById("page2").style.display = "block";

    document.getElementById("page2Btn").classList.add("active-page");
    document.getElementById("page1Btn").classList.remove("active-page");
  });

});

/* ===== Fetch Data ===== */

fetch("results.json")
  .then(res => res.json())
  .then(data => {
    screenerData = data;

    renderTable("ALL");
  });

/* ===== Custom Stock Search ===== */

document.addEventListener("input", function (e) {

  if (!e.target.classList.contains("stock-input")) return;

  const value = e.target.value.trim().toUpperCase();

  removeSuggestions();

  if (value.length < 3) return;

  const matches = screenerData
    .filter(item => item.symbol.startsWith(value))
    .slice(0, 15);

  if (matches.length === 0) return;

  const list = document.createElement("div");

  list.className = "stock-suggestions";

  matches.forEach(item => {

    const option = document.createElement("div");

    option.className = "stock-option";

    option.textContent = item.symbol;

    option.addEventListener("click", () => {

      e.target.value = item.symbol;

      removeSuggestions();

    });

    list.appendChild(option);

  });

  e.target.parentElement.style.position = "relative";

  e.target.parentElement.appendChild(list);

});

function removeSuggestions() {

  document
    .querySelectorAll(".stock-suggestions")
    .forEach(el => el.remove());

}

document.addEventListener("click", function (e) {

  if (
    !e.target.classList.contains("stock-input") &&
    !e.target.classList.contains("stock-option")
  ) {
    removeSuggestions();
  }

});

/* ===== Main Filter ===== */

document.getElementById("filter").addEventListener("change", e => {
  renderTable(e.target.value);
});

/* ===== CMP Sort ===== */

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

  const cmpSort = document.getElementById("cmpSort").value;

  if (cmpSort === "ASC") {
    dataToRender.sort((a, b) => a.cmp - b.cmp);
  }

  dataToRender.forEach(item => {

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

  document.getElementById("rowCount").textContent =
    document.querySelectorAll("#screener-table tbody tr").length;
}
