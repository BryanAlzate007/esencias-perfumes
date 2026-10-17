import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { addGuestItem, CHECKOUT_AFTER_LOGIN, lineFromQuote, readGuestCart, removeGuestItem, syncGuestCart } from "../lib/guestCart";
import { openWompiCheckout } from "../lib/wompi";
import { addToCart as addToCartRequest, getCart, removeCartItem } from "../services/orders";
import { startPayment } from "../services/payments";

export const CartContext = createContext(null);

function cartItems(data) {
  return Array.isArray(data) ? data : data.results || [];
}

export function CartProvider({ children }) {
  const navigate = useNavigate();
  const { ready, isAuthenticated, isAdmin } = useAuth();
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);

  const loadCart = useCallback(async () => {
    if (!ready || isAdmin) {
      return [];
    }
    if (!isAuthenticated) {
      return readGuestCart();
    }
    await syncGuestCart(addToCartRequest);
    return cartItems(await getCart());
  }, [ready, isAuthenticated, isAdmin]);

  const refreshCart = useCallback(async () => {
    const next = await loadCart();
    setItems(next);
    return next;
  }, [loadCart]);

  const checkout = useCallback(async () => {
    if (!isAuthenticated || isAdmin) {
      return { needsLogin: true };
    }
    await syncGuestCart(addToCartRequest);
    const session = await startPayment();
    setItems(cartItems(await getCart()));
    setOpen(false);
    try {
      await openWompiCheckout(session);
    } catch {
      // The order stays pending and can be paid again from Pedidos.
    }
    return session;
  }, [isAuthenticated, isAdmin]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const next = await loadCart();
        if (cancelled) {
          return;
        }
        setItems(next);
      } catch {
        if (!cancelled) {
          setItems(isAuthenticated ? [] : readGuestCart());
        }
        return;
      }
      if (cancelled || !isAuthenticated || sessionStorage.getItem(CHECKOUT_AFTER_LOGIN) !== "1") {
        return;
      }
      sessionStorage.removeItem(CHECKOUT_AFTER_LOGIN);
      if (isAdmin) {
        return;
      }
      try {
        const session = await checkout();
        if (!cancelled && session && !session.needsLogin) {
          navigate("/pedidos");
        }
      } catch {
        // The cart stays available so the purchase can be tried again.
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [loadCart, isAuthenticated, isAdmin, checkout, navigate]);

  const saveQuote = useCallback(
    async (quote) => {
      const line = lineFromQuote(quote);
      if (!isAuthenticated || isAdmin) {
        const next = addGuestItem(line);
        setItems(next);
        setOpen(true);
        return next;
      }
      const extra = { grams: line.grams };
      if (line.container) {
        extra.container = line.container;
      }
      await addToCartRequest(line.perfume, 1, extra);
      const next = await refreshCart();
      setOpen(true);
      return next;
    },
    [isAuthenticated, isAdmin, refreshCart],
  );

  const removeItem = useCallback(
    async (id) => {
      if (!isAuthenticated || isAdmin) {
        const next = removeGuestItem(id);
        setItems(next);
        return next;
      }
      await removeCartItem(id);
      return refreshCart();
    },
    [isAuthenticated, isAdmin, refreshCart],
  );

  const total = items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
  const count = items.reduce((sum, item) => sum + Number(item.quantity), 0);

  const value = useMemo(
    () => ({
      items,
      open,
      setOpen,
      saveQuote,
      removeItem,
      checkout,
      refreshCart,
      total,
      count,
    }),
    [items, open, saveQuote, removeItem, checkout, refreshCart, total, count],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
