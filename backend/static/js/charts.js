function portalChart(canvasId, type, labels, data, label, options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return null;

  return new Chart(canvas, {
    type,
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: [
          "#2f80ed", "#27ae60", "#f2c94c", "#eb5757",
          "#56ccf2", "#9b51e0", "#f2994a", "#6c757d"
        ],
        borderColor: "#ffffff",
        borderWidth: 1
      }]
    },
    options: Object.assign({
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } }
    }, options)
  });
}
