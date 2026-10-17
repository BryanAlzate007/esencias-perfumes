import { syncPayment } from "../services/payments";

const WOMPI_WIDGET = "https://checkout.wompi.co/widget.js";

function loadWompi() {
  if (window.WidgetCheckout) {
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    const finish = () => {
      if (window.WidgetCheckout) {
        resolve();
        return;
      }
      reject(new Error("Wompi no está disponible."));
    };
    const existing = document.querySelector(`script[src="${WOMPI_WIDGET}"]`);
    if (existing) {
      if (existing.dataset.loaded === "true") {
        finish();
        return;
      }
      existing.addEventListener("load", finish);
      existing.addEventListener("error", () =>
        reject(new Error("No se pudo cargar Wompi.")),
      );
      return;
    }
    const script = document.createElement("script");
    script.src = WOMPI_WIDGET;
    script.async = true;
    script.onload = () => {
      script.dataset.loaded = "true";
      finish();
    };
    script.onerror = () => reject(new Error("No se pudo cargar Wompi."));
    document.head.appendChild(script);
  });
}

export async function openWompiCheckout(session) {
  await loadWompi();
  const options = {
    currency: session.currency,
    amountInCents: session.amount_in_cents,
    reference: session.reference,
    publicKey: session.public_key,
    signature: { integrity: session.signature },
    redirectUrl: session.redirect_url,
    expirationTime: session.expiration_time,
  };
  if (session.customer_email) {
    options.customerData = { email: session.customer_email };
  }
  const checkout = new window.WidgetCheckout(options);
  checkout.open((result) => {
    const transactionId = result?.transaction?.id;
    if (!transactionId) {
      return;
    }
    syncPayment(transactionId)
      .catch(() => {})
      .finally(() => window.dispatchEvent(new Event("payment-updated")));
  });
}
