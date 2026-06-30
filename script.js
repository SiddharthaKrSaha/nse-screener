let screenerData = [];
let latestNews = {};

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

/* ===== NIFTY & SENSEX ===== */

function formatNumber(value) {
  return Number(value).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function isMarketTime() {

  const now = new Date();

  const day = now.getDay(); // 0=Sun, 6=Sat

  if (day === 0 || day === 6) return false;

  const minutes =
    now.getHours() * 60 + now.getMinutes();

  return minutes >= (9 * 60 + 15) &&
         minutes <= (15 * 60 + 45);

}

function displayIndices(data) {

  // ---------- Sensex ----------

  const sensexPositive = data.sensex.change >= 0;

  const sensexBox = document.getElementById("sensexBox");

  sensexBox.className =
  `index-box ${sensexPositive ? "positive-box" : "negative-box"}`;

  sensexBox.innerHTML = `
    <div class="index-title">Sensex</div>

    <div class="index-price ${sensexPositive ? "positive" : "negative"}">
      ${formatNumber(data.sensex.price)}
    </div>

    <div class="index-change ${sensexPositive ? "positive" : "negative"}">
      ${sensexPositive ? "+" : ""}${formatNumber(data.sensex.change)}
      (${data.sensex.percent.toFixed(2)}%)
    </div>
  `;

  // ---------- Nifty ----------

  const niftyPositive = data.nifty.change >= 0;

  const niftyBox = document.getElementById("niftyBox");

  niftyBox.className =
  `index-box ${niftyPositive ? "positive-box" : "negative-box"}`;

  niftyBox.innerHTML = `
    <div class="index-title">Nifty</div>

    <div class="index-price ${niftyPositive ? "positive" : "negative"}">
      ${formatNumber(data.nifty.price)}
    </div>

    <div class="index-change ${niftyPositive ? "positive" : "negative"}">
      ${niftyPositive ? "+" : ""}${formatNumber(data.nifty.change)}
      (${data.nifty.percent.toFixed(2)}%)
    </div>
  `;

}

async function loadIndices() {

  if (!isMarketTime()) {

  const saved = localStorage.getItem("indexData");

  if (saved) {
    displayIndices(JSON.parse(saved));
  }

  return;

}

  try {

    const response = await fetch(
      "https://nse-indices.vercel.app/api/indices"
    );

    const data = await response.json();

    localStorage.setItem("indexData", JSON.stringify(data));

    displayIndices(data);

  } catch (err) {

    console.log("Index data unavailable");

  }

}

// Initial load
loadIndices();

// Refresh exactly at :00, :15, :30, :45
setInterval(() => {

  const now = new Date();

  if (
    now.getSeconds() === 0 &&
    now.getMinutes() % 15 === 0
  ) {
    loadIndices();
  }

}, 1000);

/* ===== Fetch Data ===== */

Promise.all([
  fetch("results.json").then(r => r.json()),
  fetch("news.json")
])

.then(([stocks, newsData]) => {

  screenerData = stocks;

  latestNews = {};

  if (newsData.news) {

    newsData.news.forEach(item => {

      latestNews[item.symbol] = item;

    });

  }

  renderTable("ALL");

});

/* ===== Custom Stock Search ===== */

document.addEventListener("input", function (e) {

  if (!e.target.classList.contains("stock-input")) return;

  const value = e.target.value.trim().toUpperCase();

  removeSuggestions();

  if (value.length < 2) return;

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

  document.getElementById("priceBand").addEventListener("change", () => {
  renderTable(document.getElementById("filter").value);
});

  document.getElementById("newsFilter").addEventListener("change", () => {
    renderTable(document.getElementById("filter").value);
});

});

/* ===== Render Table ===== */

function renderTable(filter) {

  const tbody = document.querySelector("#screener-table tbody");

  tbody.innerHTML = "";

  let dataToRender = [...screenerData];

  const cmpSort = document.getElementById("cmpSort").value;
  const priceBand = document.getElementById("priceBand").value;
  const newsFilter = document.getElementById("newsFilter").value;

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
      (priceBand === "LT100" && item.cmp >= 100) ||
      (priceBand === "100-200" && (item.cmp < 100 || item.cmp >= 200)) ||
      (priceBand === "200-300" && (item.cmp < 200 || item.cmp >= 300)) ||
      (priceBand === "300-400" && (item.cmp < 300 || item.cmp >= 400)) ||
      (priceBand === "400-500" && (item.cmp < 400 || item.cmp >= 500)) ||
      (priceBand === "GT500" && item.cmp <= 500)
    ) return;

    if (newsFilter === "NEWS" && !latestNews[item.symbol]) {
    return;
    }

    if (
      (filter === "GREEN" && !isUp) ||
      (filter === "RED" && !isDown)
    ) return;

    const trendClass = isUp ? "trend-up" : "trend-down";

    const news = latestNews[item.symbol];

let newsHtml = "";

if (news) {

    const words = news.headline.split(" ");
  
  const shortHeadline =
    words.length > 10
        ? words.slice(0, 10).join(" ") + "..."
        : news.headline;

    newsHtml =
        `<a href="${news.url}" target="_blank" title="${news.headline}">
            ${shortHeadline}
        </a>`;
}

const row = document.createElement("tr");

row.innerHTML = `
    <td class="${trendClass}">${item.symbol}</td>
    <td class="cmp">${item.cmp}</td>
    <td class="${trendClass}">${item.trend}</td>
    <td class="news-cell">${newsHtml}</td>
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

      console.log(symbol, cmp, open);

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
        ? '<span style="font-size:20px;color:green;">🟢</span>'
        : '<span style="font-size:20px;color:red;">🔴</span>';

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

/* ===== Reset Table Button ===== */

document.getElementById("resetTableBtn")
.addEventListener("click", () => {

  const rows =
    document.querySelectorAll("#analysis-table tbody tr");

  rows.forEach(row => {

    row.querySelector(".stock-input").value = "";

    row.cells[1].innerHTML = "";
    row.cells[2].textContent = "";
    row.cells[3].textContent = "";
    row.cells[4].textContent = "";
    row.cells[5].textContent = "";
    row.cells[6].textContent = "";
    row.cells[7].textContent = "";

  });

  removeSuggestions();

});

/* ===== Lightweight Candlestick Chart ===== */

let currentChartSymbol = "";
let autoRefreshTimer = null;

let chart = null;
let candlestickSeries = null;

async function loadChart(symbol = "SBIN") {

  const response = await fetch(
    `https://nse-live-cmp.guestxolo.workers.dev/?symbol=${symbol}`
  );

  const data = await response.json();

  const candleData = data.candles;

  currentChartSymbol = symbol;

  document.getElementById("chartContainer").innerHTML = "";

  if (chart) {
  chart.remove();
}

chart = LightweightCharts.createChart(
  document.getElementById("chartContainer"),
  {
    width: 1200,
    height: 700
  }
);

candlestickSeries =
  chart.addSeries(
    LightweightCharts.CandlestickSeries
  );

candlestickSeries.setData(candleData);

chart.timeScale().fitContent();

chart.subscribeCrosshairMove(param => {

  if (!param.seriesData.size) return;

  const candle =
    param.seriesData.get(candlestickSeries);

  if (!candle) return;

  document.getElementById("ohlcInfo").textContent =
  `O: ${candle.open.toFixed(2)} | H: ${candle.high.toFixed(2)} | L: ${candle.low.toFixed(2)} | C: ${candle.close.toFixed(2)}`;

});

}

/* ===== Load Chart Button / Auto Refresh ===== */

document.getElementById("loadChartBtn")
.addEventListener("click", () => {

  const symbol =
    document.getElementById("chartSymbol")
    .value
    .trim()
    .toUpperCase();

  if (!symbol) return;

  loadChart(symbol);

});

document.getElementById("autoRefreshToggle")
.addEventListener("change", function () {

  if (this.checked) {

    autoRefreshTimer = setInterval(() => {

      loadChart(currentChartSymbol);

    }, 60000);

  } else {

    clearInterval(autoRefreshTimer);

  }

});

document.getElementById("resetChartBtn")
.addEventListener("click", () => {

  if (chart) {
    chart.remove();
    chart = null;
    candlestickSeries = null;
  }

  document.getElementById("chartContainer").innerHTML = "";

  document.getElementById("chartSymbol").value = "";

  document.getElementById("ohlcInfo").textContent =
    "O: - | H: - | L: - | C: -";

  currentChartSymbol = "";

  clearInterval(autoRefreshTimer);

  document.getElementById("autoRefreshToggle").checked = false;

});
