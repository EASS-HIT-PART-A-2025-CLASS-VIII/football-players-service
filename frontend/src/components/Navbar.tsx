import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFutbol, faBars, faXmark } from "@fortawesome/free-solid-svg-icons";
import "./Navbar.css";

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <>
      <nav className="navbar">
        <div className="navbar-container">
          <Link to="/" className="navbar-logo" onClick={closeMobileMenu}>
            <FontAwesomeIcon icon={faFutbol} className="logo-icon" />
            Football App
          </Link>

          {/* Desktop Menu */}
          <ul className="navbar-menu desktop-menu">
            <li className="navbar-item">
              <Link
                to="/"
                className={`navbar-link ${isActive("/") ? "active" : ""}`}
              >
                Home
              </Link>
            </li>
            <li className="navbar-item">
              <Link
                to="/players"
                className={`navbar-link ${
                  isActive("/players") ? "active" : ""
                }`}
              >
                Players
              </Link>
            </li>
          </ul>

          {/* Hamburger Icon */}
          <button
            className="hamburger-button"
            onClick={toggleMobileMenu}
            aria-label="Toggle menu"
          >
            <FontAwesomeIcon icon={isMobileMenuOpen ? faXmark : faBars} />
          </button>
        </div>
      </nav>

      {/* Mobile Sidebar */}
      <div
        className={`mobile-sidebar ${isMobileMenuOpen ? "open" : ""}`}
        onClick={closeMobileMenu}
      >
        <div
          className="mobile-sidebar-content"
          onClick={(e) => e.stopPropagation()}
        >
          <ul className="mobile-menu">
            <li className="mobile-menu-item">
              <Link
                to="/"
                className={`mobile-menu-link ${isActive("/") ? "active" : ""}`}
                onClick={closeMobileMenu}
              >
                Home
              </Link>
            </li>
            <li className="mobile-menu-item">
              <Link
                to="/players"
                className={`mobile-menu-link ${
                  isActive("/players") ? "active" : ""
                }`}
                onClick={closeMobileMenu}
              >
                Players
              </Link>
            </li>
          </ul>
        </div>
      </div>

      {/* Backdrop Overlay */}
      {isMobileMenuOpen && (
        <div className="mobile-backdrop" onClick={closeMobileMenu}></div>
      )}
    </>
  );
};

export default Navbar;
