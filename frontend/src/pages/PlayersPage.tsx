import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFutbol,
  faEarthEurope,
  faCakeCandles,
} from "@fortawesome/free-solid-svg-icons";
import "./PlayersPage.css";
import { formatCurrency, getStatusColor } from "../utils";

// Mock data - will be replaced with API data later
const MOCK_PLAYERS = [
  {
    id: "1",
    full_name: "Cristiano Ronaldo",
    country: "Portugal",
    status: "active" as const,
    current_team: "Al Nassr",
    league: "Saudi Pro League",
    age: 39,
    market_value: 15000000,
  },
  {
    id: "2",
    full_name: "Lionel Messi",
    country: "Argentina",
    status: "active" as const,
    current_team: "Inter Miami",
    league: "MLS",
    age: 37,
    market_value: 35000000,
  },
  {
    id: "3",
    full_name: "Kylian Mbappé",
    country: "France",
    status: "active" as const,
    current_team: "Real Madrid",
    league: "La Liga",
    age: 25,
    market_value: 180000000,
  },
  {
    id: "4",
    full_name: "Erling Haaland",
    country: "Norway",
    status: "active" as const,
    current_team: "Manchester City",
    league: "Premier League",
    age: 24,
    market_value: 170000000,
  },
  {
    id: "5",
    full_name: "Vinicius Jr.",
    country: "Brazil",
    status: "active" as const,
    current_team: "Real Madrid",
    league: "La Liga",
    age: 24,
    market_value: 150000000,
  },
  {
    id: "6",
    full_name: "Jude Bellingham",
    country: "England",
    status: "active" as const,
    current_team: "Real Madrid",
    league: "La Liga",
    age: 21,
    market_value: 180000000,
  },
];

const PlayersPage = () => {
  return (
    <div className="players-page">
      <div className="players-header">
        <div className="header-content">
          <h1 className="players-title">
            <FontAwesomeIcon icon={faFutbol} className="title-icon" />
            Player Catalog
          </h1>
          <p className="players-subtitle">
            Explore the world's top football talent
          </p>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <div className="stat-value">{MOCK_PLAYERS.length}</div>
            <div className="stat-label">Players</div>
          </div>
        </div>
      </div>

      <div className="players-grid">
        {MOCK_PLAYERS.map((player, index) => (
          <div
            key={player.id}
            className="player-card"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="card-header">
              <div className="player-avatar">{player.full_name.charAt(0)}</div>
              <span
                className={`player-status ${getStatusColor(player.status)}`}
              >
                {player.status.replace("_", " ")}
              </span>
            </div>

            <div className="card-body">
              <h3 className="player-name">{player.full_name}</h3>
              <div className="player-info">
                <span className="info-item">
                  <FontAwesomeIcon icon={faEarthEurope} className="info-icon" />
                  {player.country}
                </span>
                <span className="info-item">
                  <FontAwesomeIcon icon={faCakeCandles} className="info-icon" />
                  {player.age} yrs
                </span>
              </div>
            </div>

            <div className="card-footer">
              <div className="team-info">
                <div className="team-name">{player.current_team}</div>
                <div className="team-league">{player.league}</div>
              </div>
              <div className="market-value">
                {formatCurrency(player.market_value)}
              </div>
            </div>

            <div className="card-glow"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlayersPage;
