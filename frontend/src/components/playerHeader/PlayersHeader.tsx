import { faFutbol, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import "./PlayersHeader.css";

const PlayersHeader = ({
  count,
  onAdd,
  disabled,
}: {
  count: number;
  onAdd: () => void;
  disabled: boolean;
}) => (
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
    <div className="header-actions">
      <div className="header-stats">
        <div className="stat-item">
          <div className="stat-value">{count}</div>
          <div className="stat-label">Players</div>
        </div>
      </div>
      <button className="btn-add-player" onClick={onAdd} disabled={disabled}>
        <FontAwesomeIcon icon={faPlus} />
        <span className="btn-text">Add Player</span>
      </button>
    </div>
  </div>
);

export default PlayersHeader;
