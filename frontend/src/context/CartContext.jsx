import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { openWompiCheckout } from "../lib/wompi";
import { addToCart as addToCartRequest, getCart, removeCartItem } from "../services/orders";
import { startPayment } from "../services/payments";
import { useAuth } from "../hooks/useAuth";

export const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { isAuthenticated, isAdmin } = useAuth();
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated || isAdmin) {
      setItems([]);
      return [];
    }
    const data = await getCart();
    const next = Array.isArray(data) ? data : data.results || [];
    setItems(next);
    return next;
  }, [isAuthenticated, isAdmin]);

  useEffect(() => {
    refreshCart().catch(() => setItems([]));
  }, [refreshCart]);

  const addItem = useCallback(
    async (perfumeId) => {
      await addToCartRequest(perfumeId);
      const next = await refreshCart();
      setOpen(true);
      return next;
    },
    [refreshCart],
  );

  const removeItem = useCallback(
    async (id) => {
      await removeCartItem(id);
      return refreshCart();
    },
    [refreshCart],
  );

  const checkout = useCallback(async () => {
    const session = await startPayment();
    await refreshCart();
    setOpen(false);
    try {
      await openWompiCheckout(session);
    } catch {
      // The order stays pending and can be paid again from Pedidos.
    }
    return session;
  }, [refreshCart]);

  const total = items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
  const count = items.reduce((sum, item) => sum + item.quantity, 0);

  const value = useMemo(
    () => ({
      items,
      open,
      setOpen,
      addItem,
      removeItem,
      checkout,
      refreshCart,
      total,
      count,
    }),
    [items, open, addItem, removeItem, checkout, refreshCart, total, count],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
