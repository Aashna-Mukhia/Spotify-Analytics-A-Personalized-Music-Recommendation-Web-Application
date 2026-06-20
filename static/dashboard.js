document.addEventListener("DOMContentLoaded", () => {

  // ── Tab Navigation ─────────────────────────────────
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
  });

  // ── Charts ─────────────────────────────────────────
  const chartEl = document.getElementById("chart-data");
  if (!chartEl) return;
  const data = JSON.parse(chartEl.textContent);

  const spotifyGreen = "#1DB954";
  const gridColor = "rgba(255,255,255,0.06)";
  const labelColor = "#b3b3b3";

  Chart.defaults.color = labelColor;
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 12;

  // Radar – Taste Profile
  const featureCanvas = document.getElementById("featuresChart");
  if (featureCanvas) {
    new Chart(featureCanvas, {
      type: "radar",
      data: {
        labels: data.featureLabels,
        datasets: [{
          label: "Your Taste",
          data: data.featureValues,
          fill: true,
          backgroundColor: "rgba(29,185,84,0.12)",
          borderColor: spotifyGreen,
          borderWidth: 2,
          pointBackgroundColor: spotifyGreen,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        animation: { duration: 800, easing: "easeOutQuart" },
        interaction: { mode: "nearest" },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${Math.round(ctx.raw * 100)}%`
            }
          }
        },
        scales: {
          r: {
            suggestedMin: 0,
            suggestedMax: 1,
            grid: { color: gridColor },
            angleLines: { color: gridColor },
            ticks: { display: false },
            pointLabels: { color: labelColor, font: { size: 11 } }
          }
        }
      }
    });
  }

  // Bar – Genre Breakdown
  const genreCanvas = document.getElementById("genreChart");
  if (genreCanvas) {
    new Chart(genreCanvas, {
      type: "bar",
      data: {
        labels: data.genreLabels,
        datasets: [{
          label: "Count",
          data: data.genreValues,
          backgroundColor: "rgba(29,185,84,0.18)",
          borderColor: spotifyGreen,
          borderWidth: 1.5,
          borderRadius: 6,
          hoverBackgroundColor: "rgba(29,185,84,0.35)"
        }]
      },
      options: {
        responsive: true,
        animation: { duration: 700, easing: "easeOutQuart" },
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: labelColor } },
          y: {
            beginAtZero: true,
            grid: { color: gridColor },
            ticks: { precision: 0, color: labelColor }
          }
        }
      }
    });
  }

});
