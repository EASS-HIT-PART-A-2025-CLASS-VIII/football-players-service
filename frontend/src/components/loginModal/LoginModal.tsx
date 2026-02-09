import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import { login } from "../../services/api";
import "./LoginModal.css";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: () => void;
}

const LoginModal = ({ isOpen, onClose, onLoginSuccess }: LoginModalProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [attemptCount, setAttemptCount] = useState(0);
  const usernameRef = useRef<HTMLInputElement>(null);

  // Clear error when user starts typing
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
    if (error) setError(null);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (error) setError(null);
  };

  // Focus username input when modal opens
  useEffect(() => {
    if (isOpen && usernameRef.current) {
      usernameRef.current.focus();
    }
  }, [isOpen]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setError(null);
      setAttemptCount(0);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await login(username, password);
      localStorage.setItem("access_token", response.access_token);
      onLoginSuccess();
      // Reset form
      setUsername("");
      setPassword("");
      setAttemptCount(0);
      onClose();
    } catch (err) {
      console.error("Login failed:", err);
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      const newAttemptCount = attemptCount + 1;
      setAttemptCount(newAttemptCount);

      if (axiosError.response?.status === 401) {
        const serverMessage = axiosError.response?.data?.detail;
        if (serverMessage) {
          setError(serverMessage);
        } else if (newAttemptCount >= 3) {
          setError("Invalid credentials. Please check your username and password carefully.");
        } else {
          setError("Incorrect username or password. Please try again.");
        }
      } else if (axiosError.response?.status === 422) {
        setError("Please enter a valid username and password.");
      } else if (!axiosError.response) {
        setError("Unable to connect to server. Please check your connection.");
      } else {
        setError("Something went wrong. Please try again later.");
      }

      // Focus password field for quick retry
      if (password) {
        setPassword("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isLoading) {
      onClose();
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="login-modal-backdrop" onClick={handleBackdropClick}>
      <div className="login-modal-container">
        <button
          className="login-modal-close"
          onClick={handleClose}
          aria-label="Close"
          disabled={isLoading}
        >
          ×
        </button>

        <div className="login-modal-header">
          <h2>Sign In</h2>
          <p className="login-modal-subtitle">Access the Scouting Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="login-modal-form">
          <div className={`login-modal-field ${error ? "login-modal-field--error" : ""}`}>
            <label htmlFor="modal-username">Username</label>
            <input
              ref={usernameRef}
              id="modal-username"
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Enter username"
              disabled={isLoading}
              aria-invalid={!!error}
            />
          </div>

          <div className={`login-modal-field ${error ? "login-modal-field--error" : ""}`}>
            <label htmlFor="modal-password">Password</label>
            <input
              id="modal-password"
              type="password"
              value={password}
              onChange={handlePasswordChange}
              placeholder="Enter password"
              disabled={isLoading}
              aria-invalid={!!error}
            />
          </div>

          {error && (
            <div className="login-modal-error" role="alert">
              <span className="login-modal-error-icon">!</span>
              <span className="login-modal-error-text">{error}</span>
            </div>
          )}

          <button
            type="submit"
            className={`login-modal-button ${isLoading ? "login-modal-button--loading" : ""}`}
            disabled={isLoading || !username || !password}
          >
            {isLoading ? (
              <>
                <span className="login-modal-spinner"></span>
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>
      </div>
    </div>,
    document.body
  );
};

export default LoginModal;
