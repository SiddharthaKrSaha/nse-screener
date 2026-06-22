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

  const selectedSymbols = Array.from(
  document.querySelectorAll(".stock-input")
)
.map(input => input.value.trim().toUpperCase())
.filter(v => v !== "");

const matches = screenerData
  .filter(item =>
    item.symbol.startsWith(value) &&
    !selectedSymbols.includes(item.symbol)
  )
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

/* ===== Prevent Duplicate Stocks ===== */

document.addEventListener("change", function (e) {

  if (!e.target.classList.contains("stock-input")) return;

  const currentValue = e.target.value.trim().toUpperCase();

  if (!currentValue) return;

  const allInputs = document.querySelectorAll(".stock-input");

  let duplicateCount = 0;

  allInputs.forEach(input => {

    if (input.value.trim().toUpperCase() === currentValue) {
      duplicateCount++;
    }

  });

  if (duplicateCount > 1) {

    alert("This stock is already selected.");

    e.target.value = "";

  }

});

/* ===== Analyze Button ===== */

document.getElementById("analyzeBtn").addEventListener("click", async () => {

  const rows = document.querySelectorAll("#analysis-table tbody tr");

  for (const row of rows) {

    const symbol = row.querySelector(".stock-input").value.trim().toUpperCase();

    if (!symbol) continue;

    const stock = screenerData.find(
      item => item.symbol === symbol
    );

    if (!stock) continue;

    try {

      const response = await fetch(
        `https://nse-live-cmp.guestxolo.workers.dev/?symbol=${symbol}`
      );

      const liveData = await response.json();

      const cmp = liveData.cmp;

      const open = liveData.open;

      const gapPercent =
        ((cmp - open) / open) * 100;

      const gapHtml =
        gapPercent >= 0
          ? `<span style="color:green;font-weight:bold;">+${gapPercent.toFixed(2)}%</span>`
          : `<span style="color:red;font-weight:bold;">${gapPercent.toFixed(2)}%</span>`;

      let p4 = "-";

      if (
        stock.trend === "UPWARD" &&
        cmp > stock.last_green_open
      ) {
        p4 = "Match";
      }

      if (
        stock.trend === "DOWNWARD" &&
        cmp < stock.last_red_open
      ) {
        p4 = "Match";
      }

      row.cells[1].innerHTML =
        stock.trend === "UPWARD"
          ? '<span style="color:green;font-weight:bold;">UPWARD</span>'
          : '<span style="color:red;font-weight:bold;">DOWNWARD</span>';

      row.cells[2].textContent = cmp;
      row.cells[3].innerHTML = gapHtml;
      row.cells[4].textContent = p4;
      row.cells[5].textContent = "Check BToD Manually";
      row.cells[6].textContent = "Check L15M Manually";
      row.cells[7].textContent = "Check OoBT Manually";

    } catch (err) {

      row.cells[2].textContent = "API Error";

    }

  }

});

new TradingView.widget({
  "autosize": true,
  "symbol": "NSE:SBIN",
  "interval": "15",
  "timezone": "Asia/Kolkata",
  "theme": "light",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_chart"
});
