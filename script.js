fetch("results.json")
  .then(res => res.json())
  .then(data => {
    const tbody = document.querySelector("#screener-table tbody");
    tbody.innerHTML = "";

    data.forEach(item => {
      const row = document.createElement("tr");

      const trendClass =
        item.monthly === "UP" && item.weekly === "UP" && item.daily === "UP"
          ? "trend-up"
          : "trend-down";

      row.innerHTML = `
        <td class="${trendClass}">${item.symbol}</td>
        <td class="cmp">${item.cmp}</td>
        <td class="${trendClass}">${item.monthly}</td>
        <td class="${trendClass}">${item.weekly}</td>
        <td class="${trendClass}">${item.daily}</td>
      `;

      tbody.appendChild(row);
    });
  });
