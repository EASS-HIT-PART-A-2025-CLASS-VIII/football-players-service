import { useNavigate, useOutletContext } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFutbol,
  faTrophy,
  faChartSimple,
  faEarthEurope,
  faArrowTrendUp,
  faBolt,
} from "@fortawesome/free-solid-svg-icons";
import { faGem } from "@fortawesome/free-regular-svg-icons";
import type { RootLayoutContext } from "../../layouts/RootLayout";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, onOpenLogin } =
    useOutletContext<RootLayoutContext>();

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <FontAwesomeIcon icon={faBolt} className="badge-icon" />
            <span>Your Ultimate Football Hub</span>
          </div>

          <h1 className="hero-title">
            Watch Your <span className="hero-highlight">Favorite</span> Football
            Players
          </h1>

          <p className="hero-description">
            Discover stats, profiles, and insights from the world's top football
            players. Stay connected with the legends of the game.
          </p>

          {isAuthenticated ? (
            <button className="cta-button" onClick={() => navigate("/players")}>
              <span className="cta-text">Explore Players</span>
              <span className="cta-arrow">→</span>
            </button>
          ) : (
            <button className="cta-button" onClick={onOpenLogin}>
              <span className="cta-text">Sign In</span>
              <span className="cta-arrow">→</span>
            </button>
          )}
        </div>

        <div className="hero-decoration">
          <div className="floating-card card-1">
            <FontAwesomeIcon icon={faFutbol} className="card-icon" />
            <div className="card-label">Live Stats</div>
          </div>
          <div className="floating-card card-2">
            <FontAwesomeIcon icon={faTrophy} className="card-icon" />
            <div className="card-label">Achievements</div>
          </div>
          <div className="floating-card card-3">
            <FontAwesomeIcon icon={faChartSimple} className="card-icon" />
            <div className="card-label">Analytics</div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="feature-card">
          <FontAwesomeIcon icon={faEarthEurope} className="feature-icon" />
          <h3 className="feature-title">Global Database</h3>
          <p className="feature-text">Access players from leagues worldwide</p>
        </div>

        <div className="feature-card">
          <FontAwesomeIcon icon={faArrowTrendUp} className="feature-icon" />
          <h3 className="feature-title">Real-Time Data</h3>
          <p className="feature-text">Up-to-date stats and market values</p>
        </div>

        <div className="feature-card">
          <FontAwesomeIcon icon={faGem} className="feature-icon" />
          <h3 className="feature-title">Premium Insights</h3>
          <p className="feature-text">
            Deep analysis of player performance with AI scout reports
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
