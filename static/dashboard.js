document.addEventListener("DOMContentLoaded", () => {
  const chartEl = document.getElementById("chart-data");
  if (!chartEl) return;

  const data = JSON.parse(chartEl.textContent);

  const featureCanvas = document.getElementById("featuresChart");
  if (featureCanvas) {
    new Chart(featureCanvas, {
      type: "radar",
      data: {
        labels: data.featureLabels,
        datasets: [{
          label: "Average Audio Features",
          data: data.featureValues,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { r: { suggestedMin: 0, suggestedMax: 1 } }
      }
    });
  }

  const genreCanvas = document.getElementById("genreChart");
  if (genreCanvas) {
    new Chart(genreCanvas, {
      type: "bar",
      data: {
        labels: data.genreLabels,
        datasets: [{
          label: "Genre Count",
          data: data.genreValues
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }
});
