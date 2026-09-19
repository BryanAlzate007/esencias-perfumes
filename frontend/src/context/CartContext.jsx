import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { addToCart as addToCartRequest, checkout as checkoutRequest, getCart, removeCartItem } from "../services/orders";
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
    const order = await checkoutRequest();
    await refreshCart();
    setOpen(false);
    return order;
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
