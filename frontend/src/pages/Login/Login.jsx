import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuthModal } from "../../hooks/useAuthModal";

export default function Login() {
  const { openLogin } = useAuthModal();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    openLogin(location.state?.from || "/");
    navigate("/", { replace: true });
  }, [location.state, navigate, openLogin]);

  return null;
}
