const map = L.map("map").setView([20, 78], 4);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "&copy; OpenStreetMap contributors" }).addTo(map);
let featureLayer;

const form = document.getElementById("upload-form");
const statusBox = document.getElementById("status");
const measurementsBody = document.getElementById("measurements");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = document.getElementById("file-input").files[0];
  if (!file) return;

  const button = form.querySelector("button");
  button.disabled = true;
  setStatus("Uploading and processing…");

  try {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("/api/files/", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed.");

    renderFileInfo(data);
    await Promise.all([loadGeoJson(data.id), loadMeasurements(data.id)]);
    setStatus("Processing completed successfully.");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    button.disabled = false;
  }
});

async function loadGeoJson(id) {
  const response = await fetch(`/api/files/${id}/geojson`);
  if (!response.ok) throw new Error("Unable to load feature geometry.");
  const geojson = await response.json();
  if (featureLayer) map.removeLayer(featureLayer);
  featureLayer = L.geoJSON(geojson, {
    onEachFeature: (feature, layer) => {
      const properties = feature.properties || {};
      const content = Object.entries(properties).map(([k,v]) => `<b>${escapeHtml(k)}</b>: ${escapeHtml(String(v))}`).join("<br>");
      if (content) layer.bindPopup(content);
    }
  }).addTo(map);
  if (featureLayer.getBounds().isValid()) map.fitBounds(featureLayer.getBounds(), { padding: [20, 20] });
}

async function loadMeasurements(id) {
  const response = await fetch(`/api/files/${id}/measurements`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Unable to calculate measurements.");
  document.getElementById("measurement-count").textContent = `${data.measurements.length} features`;
  measurementsBody.innerHTML = data.measurements.map(item => `
    <tr><td>${escapeHtml(item.feature_id)}</td><td>${escapeHtml(item.geometry_type)}</td>
    <td>${item.area == null ? "—" : `${formatNumber(item.area)} ${item.area_unit}`}</td>
    <td>${item.length == null ? "—" : `${formatNumber(item.length)} ${item.length_unit}`}</td></tr>
  `).join("");
}

function renderFileInfo(data) {
  document.getElementById("feature-count").textContent = `${data.feature_count} features`;
  document.getElementById("file-info").innerHTML = `
    <dt>Filename</dt><dd>${escapeHtml(data.filename)}</dd>
    <dt>CRS</dt><dd>${escapeHtml(data.crs)}</dd>
    <dt>Geometry</dt><dd>${data.geometry_types.map(escapeHtml).join(", ")}</dd>
    <dt>Status</dt><dd>${escapeHtml(data.status)}</dd>
  `;
}

function setStatus(message, error = false) {
  statusBox.hidden = false;
  statusBox.textContent = message;
  statusBox.style.background = error ? "#fff0f0" : "#eef4ff";
  statusBox.style.color = error ? "#a12525" : "#214c9a";
}

function formatNumber(value) { return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 }); }
function escapeHtml(value) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;"); }
