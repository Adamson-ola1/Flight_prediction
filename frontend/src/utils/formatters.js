export function formatCurrency(value, currency = "USD") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

export function pad2(n) {
  return String(n).padStart(2, "0");
}
