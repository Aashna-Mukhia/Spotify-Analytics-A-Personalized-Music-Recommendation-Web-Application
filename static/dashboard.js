document.addEventListener("DOMContentLoaded", () => {
  const chartEl = document.getElementById("chart-data");
  if (!chartEl) return;

  const data = JSON.parse(chartEl.textContent);

  // Radar chart for Spotify audio features
  const featureCanvas = document.getElementById("featuresChart");

  if (featureCanvas) {
    new Chart(featureCanvas, {
      type: "radar",
      data: {
        labels: data.featureLabels,
        datasets: [{
          label: "Average Audio Features",
          data: data.featureValues,
          fill: true,
          backgroundColor: "rgba(236,72,153,0.2)",
          borderColor: "rgba(236,72,153,1)",
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: "top"
          },
          title: {
            display: true,
            text: "Spotify Audio Feature Analysis"
          }
        },
        scales: {
          r: {
            suggestedMin: 0,
            suggestedMax: 1
          }
        }
      }
    });
  }

  // Genre distribution visualization
  const genreCanvas = document.getElementById("genreChart");

  if (genreCanvas) {
    new Chart(genreCanvas, {
      type: "bar",
      data: {
        labels: data.genreLabels,
        datasets: [{
          label: "Genre Count",
          data: data.genreValues,
          backgroundColor: [
            "#ec4899",
            "#8b5cf6",
            "#3b82f6",
            "#14b8a6",
            "#f59e0b",
            "#ef4444",
            "#22c55e"
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true
          },
          title: {
            display: true,
            text: "Genre Distribution"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });
  }
});