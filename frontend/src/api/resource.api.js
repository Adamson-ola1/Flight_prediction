import apiClient from "./client.js";

export function predictFlightPrice(flight) {
  return apiClient.post("/api/predict", flight);
}

export function predictFlightPricesBatch(flights) {
  return apiClient.post("/api/predict/batch", { flights });
}

export function getModelMetrics() {
  return apiClient.get("/api/metrics");
}

export function getHealth() {
  return apiClient.get("/health");
}
