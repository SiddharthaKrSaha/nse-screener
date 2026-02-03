fetch("results.json")
  .then(res => res.json())
  .then(data => {
    const tbody = document.querySelector("#screener-table tbody");
    tbody.innerHTML = "";

    data.forEach(item => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${item.symbol}</td>
        <td>${item.cmp}</td>
        <td></td>
        <td></td>
        <td></td>
      `;

      tbody.appendChild(row);
    });
  });
