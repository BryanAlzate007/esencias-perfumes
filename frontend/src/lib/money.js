export function formatMoney(value, language) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "";
  }
  const english = String(language || "").toLowerCase().startsWith("en");
  const cents = Math.round(Math.abs(amount) * 100) % 100;
  const formatted = new Intl.NumberFormat(english ? "en-US" : "es-CO", {
    minimumFractionDigits: cents ? 2 : 0,
    maximumFractionDigits: cents ? 2 : 0,
  }).format(amount);
  return `${formatted} ${english ? "USD" : "CO"}`;
}
