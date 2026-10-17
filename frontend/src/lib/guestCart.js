const STORAGE_KEY = "esencias.guestCart";

export const CHECKOUT_AFTER_LOGIN = "esencias.checkout";

export function readGuestCart() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function writeGuestCart(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function clearGuestCart() {
  localStorage.removeItem(STORAGE_KEY);
}

let syncingGuestCart = null;

export function syncGuestCart(addToCart) {
  if (syncingGuestCart) {
    return syncingGuestCart;
  }
  const guestItems = readGuestCart();
  if (!guestItems.length) {
    return Promise.resolve();
  }
  syncingGuestCart = (async () => {
    try {
      for (const item of guestItems) {
        const extra = { grams: item.grams };
        if (item.container) {
          extra.container = item.container;
        }
        await addToCart(item.perfume, item.container ? 1 : item.quantity, extra);
        writeGuestCart(readGuestCart().filter((line) => line.id !== item.id));
      }
    } finally {
      syncingGuestCart = null;
    }
  })();
  return syncingGuestCart;
}

export function addGuestItem(line) {
  const items = readGuestCart();
  const index = items.findIndex((item) => item.perfume === line.perfume && item.container === line.container);
  if (index === -1) {
    items.push(line);
  } else if (line.container) {
    items[index] = { ...items[index], ...line, id: items[index].id, quantity: 1 };
  } else {
    items[index] = {
      ...items[index],
      quantity: Number(items[index].quantity) + 1,
      price: line.price,
    };
  }
  writeGuestCart(items);
  return items;
}

export function removeGuestItem(id) {
  const items = readGuestCart().filter((item) => String(item.id) !== String(id));
  writeGuestCart(items);
  return items;
}

export function lineFromQuote(quote) {
  const container = quote.containers.find((item) => item.id === quote.selected_container) || null;
  const containerId = quote.selected_container ?? null;
  return {
    id: `guest-${quote.perfume.id}-${containerId ?? "base"}`,
    perfume: quote.perfume.id,
    perfume_name: quote.perfume.name,
    brand: quote.perfume.brand || "",
    image_url: quote.perfume.image_url,
    container: containerId,
    container_name: container?.name || "",
    grams: quote.grams,
    price: quote.total,
    quantity: 1,
  };
}
