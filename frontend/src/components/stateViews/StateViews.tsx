import {
  faExclamationTriangle,
  faSpinner,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./StateViews.css";

export const LoadingView = () => (
  <div className="loading-container">
    <FontAwesomeIcon icon={faSpinner} className="loading-spinner" />
    <p className="loading-text">Loading players...</p>
  </div>
);

export const ErrorView = ({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry: () => void;
}) => (
  <div className="error-container">
    <FontAwesomeIcon icon={faExclamationTriangle} className="error-icon" />
    <h3 className="error-title">Oops! Something went wrong</h3>
    <p className="error-message">
      {error instanceof Error ? error.message : "Failed to load players."}
    </p>
    <button className="retry-button" onClick={onRetry}>
      Retry
    </button>
  </div>
);
