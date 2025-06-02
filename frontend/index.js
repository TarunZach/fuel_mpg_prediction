let currentModel = 'regression';

// Range input handlers for regression form
document.getElementById('engineDispl').oninput = function () {
  document.getElementById('engineDisplValue').textContent = this.value;
};
document.getElementById('cylinders').oninput = function () {
  document.getElementById('cylindersValue').textContent = this.value;
};

// Range input handlers for clustering form
document.getElementById('clusterEngineDispl').oninput = function () {
  document.getElementById('clusterEngineDisplValue').textContent = this.value;
};
document.getElementById('clusterCylinders').oninput = function () {
  document.getElementById('clusterCylindersValue').textContent = this.value;
};

function switchTab(model, event) {
  currentModel = model;

  // Update tab buttons
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  if (event && event.target) event.target.classList.add('active');

  // Hide all tab content
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  // Show the appropriate form and output
  if (model === 'regression') {
    document.getElementById('regressionForm').classList.add('active');
    document.getElementById('regressionResultsOutput').classList.add('active');
  } else if (model === 'clustering') {
    document.getElementById('clusteringForm').classList.add('active');
    document.getElementById('clusteringResultsOutput').classList.add('active');
  }
}

function makePrediction() {
  let formData;

  if (currentModel === 'regression') {
    // Get data from regression form
    formData = {
      engineDispl: parseFloat(document.getElementById('engineDispl').value),
      cylinders: parseInt(document.getElementById('cylinders').value),
      transmission: document.getElementById('transmission').value,
      driveSys: document.getElementById('driveSys').value,
      carClass: document.getElementById('carClass').value,
      smartway: document.getElementById('smartway').checked,
      fuelType: document.getElementById('fuelType').value
    };
    predictMPG(formData);
  } else {
    // Get data from clustering form
    formData = {
      engineDispl: parseFloat(document.getElementById('clusterEngineDispl').value),
      cylinders: parseInt(document.getElementById('clusterCylinders').value),
      transmission: document.getElementById('clusterTransmission').value,
      driveSys: document.getElementById('clusterDriveSys').value,
      carClass: document.getElementById('clusterCarClass').value,
      smartway: document.getElementById('clusterSmartway').checked,
      fuelType: document.getElementById('clusterFuelType').value
    };
    predictCluster(formData);
  }
}

function predictMPG(data) {
  fetch("http://127.0.0.1:5000/predict_mpg", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(result => {
      if (result.error) {
        document.getElementById('mpgResult').innerHTML = `<div class="result-error">Error: ${result.error}</div>`;
        return;
      }
      document.getElementById('mpgResult').innerHTML = `
        <div class="result-value">${result.mpg}</div>
        <div style="font-size: 1.1em; margin-bottom: 15px;">Miles Per Gallon (City)</div>
        <div class="result-label">${result.label}</div>
      `;
    })
    .catch(err => {
      console.error("API error:", err);
      document.getElementById('mpgResult').innerHTML = `<div class="result-error">Failed to connect to server.</div>`;
    });
}

function predictCluster(data) {
  fetch("http://127.0.0.1:5000/predict_cluster", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(result => {
      if (result.error) {
        document.getElementById('clusterResult').innerHTML = `<div class="result-error">Error: ${result.error}</div>`;
        return;
      }

      const clusterIndex = result.cluster;
      const clusters = [
        { name: "Economy Compact", description: "Small, fuel-efficient vehicles" },
        { name: "Mid-size Sedan", description: "Balanced performance and efficiency" },
        { name: "Luxury SUV", description: "Large, feature-rich vehicles" },
        { name: "Performance Sport", description: "High-performance vehicles" },
        { name: "Utility Truck", description: "Work and utility vehicles" }
      ];

      const assigned = clusters[clusterIndex % clusters.length];
      document.getElementById('clusterResult').innerHTML = `
        <div class="result-value">Cluster ${clusterIndex + 1}</div>
        <div style="font-size: 1.2em; margin-bottom: 15px; color:white;">${assigned.name}</div>
        <div class="cluster-info">
          <h4>Cluster Characteristics:</h4>
          <p>${assigned.description}</p>
          <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
        </div>
      `;

      const similarVehicles = [
        `${data.carClass} with ${data.cylinders}-cylinder engine`,
        `Fuel type: ${data.fuelType}`,
        `Drive system: ${data.driveSys}`,
        `Transmission: ${data.transmission}`
      ];

      document.getElementById('similarVehicles').innerHTML =
        "<div class='similar-vehicles'>" +
        similarVehicles.map(v => `<div class="vehicle-item">🚗 ${v}</div>`).join('') +
        "</div>";
    })
    .catch(err => {
      console.error("API error:", err);
      document.getElementById('clusterResult').innerHTML = `<div class="result-error">Failed to connect to server.</div>`;
    });
}