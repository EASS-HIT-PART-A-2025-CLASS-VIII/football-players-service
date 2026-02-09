import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEarthEurope,
  faCakeCandles,
  faPencil,
  faTrash,
  faSearch,
} from "@fortawesome/free-solid-svg-icons";
import { formatCurrency, getStatusColor } from "../../utils";
import type { Player } from "../../types";
import DeleteConfirmModal from "../deleteConfirmModal/DeleteConfirmModal";
import "./PlayerCard.css";

interface PlayerCardProps {
  player: Player;
  index: number;
  onEdit: (player: Player) => void;
  onDelete: (id: number) => void;
  onScout: () => void;
  isLoading: boolean;
}

const PlayerCard = ({
  player,
  index,
  onEdit,
  onDelete,
  onScout,
  isLoading,
}: PlayerCardProps) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDeleteClick = () => {
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    onDelete(player.id);
    setShowDeleteModal(false);
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
  };

  return (
    <div className="player-card" style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="card-header">
        <div className="player-avatar">{player.full_name.charAt(0)}</div>
      </div>

      <div className="card-body">
        <div className="player-name-row">
          <h3 className="player-name">{player.full_name}</h3>
          <span className={`player-status ${getStatusColor(player.status)}`}>
            {player.status.replace("_", " ")}
          </span>
        </div>
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
          <div className="team-name">{player.current_team || "N/A"}</div>
          <div className="team-league">{player.league || "N/A"}</div>
        </div>
        <div className="market-value">
          {player.market_value !== null && player.market_value !== undefined
            ? formatCurrency(player.market_value)
            : "N/A"}
        </div>
      </div>

      <div className="card-actions">
        <button
          className="card-action-btn scout-btn"
          onClick={onScout}
          disabled={isLoading}
          aria-label="Scout player"
          title={
            player.scouting_report
              ? "View scout report"
              : "Generate scout report"
          }
        >
          <FontAwesomeIcon icon={faSearch} />
        </button>
        <button
          className="card-action-btn edit-btn"
          onClick={() => onEdit(player)}
          disabled={isLoading}
          aria-label="Edit player"
        >
          <FontAwesomeIcon icon={faPencil} />
        </button>
        <button
          className="card-action-btn delete-btn"
          onClick={handleDeleteClick}
          disabled={isLoading}
          aria-label="Delete player"
        >
          <FontAwesomeIcon icon={faTrash} />
        </button>
      </div>

      <div className="card-glow"></div>

      <DeleteConfirmModal
        isOpen={showDeleteModal}
        playerName={player.full_name}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        isLoading={isLoading}
      />
    </div>
  );
};

export default PlayerCard;
