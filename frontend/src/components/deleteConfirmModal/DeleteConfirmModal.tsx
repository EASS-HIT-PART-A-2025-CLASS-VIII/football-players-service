import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import "./DeleteConfirmModal.css";

interface DeleteConfirmModalProps {
  isOpen: boolean;
  playerName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const DeleteConfirmModal = ({
  isOpen,
  playerName,
  onConfirm,
  onCancel,
  isLoading = false,
}: DeleteConfirmModalProps) => {
  if (!isOpen) return null;

  return (
    <>
      <div className="delete-modal-backdrop" onClick={onCancel}></div>
      <div className="delete-modal">
        <div className="delete-modal-icon">
          <FontAwesomeIcon icon={faExclamationTriangle} />
        </div>
        <h3 className="delete-modal-title">Are you sure?</h3>
        <p className="delete-modal-message">
          Do you really want to delete <strong>{playerName}</strong>? This
          action cannot be undone.
        </p>
        <div className="delete-modal-actions">
          <button
            className="delete-modal-btn cancel-btn"
            onClick={onCancel}
            disabled={isLoading}
          >
            No, Cancel
          </button>
          <button
            className="delete-modal-btn confirm-btn"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? "Deleting..." : "Yes, Delete"}
          </button>
        </div>
      </div>
    </>
  );
};

export default DeleteConfirmModal;
