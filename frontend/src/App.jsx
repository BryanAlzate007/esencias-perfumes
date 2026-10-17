import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { AuthModalProvider } from "./context/AuthModalContext";
import { CartProvider } from "./context/CartContext";
import { ThemeProvider } from "./context/ThemeContext";
import LoginModal from "./components/LoginModal/LoginModal";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <AuthModalProvider>
            <CartProvider>
              <AppRoutes />
              <LoginModal />
            </CartProvider>
          </AuthModalProvider>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
