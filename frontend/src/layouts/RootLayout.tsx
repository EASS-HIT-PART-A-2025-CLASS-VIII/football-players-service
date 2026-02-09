import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Navbar from "../components/navbar/Navbar";
import Footer from "../components/footer/Footer";
import LoginModal from "../components/loginModal/LoginModal";
import "./RootLayout.css";

export interface RootLayoutContext {
  isAuthenticated: boolean;
  onOpenLogin: () => void;
}

const RootLayout = () => {
  const location = useLocation();

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Initialize based on localStorage token
    return !!localStorage.getItem("access_token");
  });

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(() => {
    // Auto-open modal if redirected from protected route
    const token = localStorage.getItem("access_token");
    return !!(location.state?.requiresAuth && !token);
  });

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setIsAuthenticated(false);
  };

  const handleOpenLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const handleCloseLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  const outletContext: RootLayoutContext = {
    isAuthenticated,
    onOpenLogin: handleOpenLoginModal,
  };

  return (
    <div className="root-layout">
      <Navbar
        isAuthenticated={isAuthenticated}
        onLogout={handleLogout}
        onOpenLogin={handleOpenLoginModal}
      />
      <main className="main-content">
        <Outlet context={outletContext} />
      </main>
      <Footer />
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={handleCloseLoginModal}
        onLoginSuccess={handleLoginSuccess}
      />
    </div>
  );
};

export default RootLayout;
