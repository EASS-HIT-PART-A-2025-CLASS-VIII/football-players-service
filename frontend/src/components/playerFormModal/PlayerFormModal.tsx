import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark, faSpinner } from "@fortawesome/free-solid-svg-icons";
import {
  PlayingStatusSchema,
  type Player,
  type PlayerCreate,
} from "../../types";
import "./PlayerFormModal.css";

interface PlayerFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PlayerCreate) => Promise<void>;
  initialData?: Player;
  isLoading?: boolean;
}

const PlayerFormModal = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  isLoading = false,
}: PlayerFormModalProps) => {
  const [formData, setFormData] = useState<PlayerCreate>({
    full_name: "",
    country: "",
    status: "active",
    current_team: null,
    league: null,
    age: 18,
    market_value: null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        full_name: initialData.full_name,
        country: initialData.country,
        status: initialData.status,
        current_team: initialData.current_team ?? null,
        league: initialData.league ?? null,
        age: initialData.age,
        market_value: initialData.market_value ?? null,
      });
    }
  }, [initialData, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (formData.full_name.length < 2) {
      newErrors.full_name = "Full name must be at least 2 characters";
    }
    if (formData.country.length < 2) {
      newErrors.country = "Country must be at least 2 characters";
    }
    if (formData.age < 0 || formData.age > 120) {
      newErrors.age = "Age must be between 0 and 120";
    }
    if (
      formData.market_value !== null &&
      formData.market_value !== undefined &&
      formData.market_value < 0
    ) {
      newErrors.market_value = "Market value cannot be negative";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      setFormData({
        full_name: "",
        country: "",
        status: "active",
        current_team: null,
        league: null,
        age: 18,
        market_value: null,
      });
      setErrors({});
      onClose();
    } catch (error) {
      console.error("Form submission error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;

    let processedValue: string | number | null = value;

    if (name === "age") {
      processedValue = value === "" ? 0 : parseInt(value) || 0;
    } else if (name === "market_value") {
      processedValue = value === "" ? null : parseInt(value) || null;
    } else if (name === "current_team" || name === "league") {
      processedValue = value === "" ? null : value;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  if (!isOpen) return null;

  const isEditing = !!initialData;

  return (
    <>
      <div className="form-modal-backdrop" onClick={onClose}></div>
      <div className="form-modal">
        <div className="form-modal-header">
          <h2 className="form-modal-title">
            {isEditing ? "Edit Player" : "Add New Player"}
          </h2>
          <button
            className="form-modal-close"
            onClick={onClose}
            disabled={isSubmitting || isLoading}
            aria-label="Close modal"
          >
            <FontAwesomeIcon icon={faXmark} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="form-modal-body">
          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name *
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              placeholder="e.g., Cristiano Ronaldo"
              className={`form-input ${errors.full_name ? "error" : ""}`}
              disabled={isSubmitting || isLoading}
            />
            {errors.full_name && (
              <span className="form-error">{errors.full_name}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="country" className="form-label">
              Country *
            </label>
            <input
              type="text"
              id="country"
              name="country"
              value={formData.country}
              onChange={handleInputChange}
              placeholder="e.g., Portugal"
              className={`form-input ${errors.country ? "error" : ""}`}
              disabled={isSubmitting || isLoading}
            />
            {errors.country && (
              <span className="form-error">{errors.country}</span>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="status" className="form-label">
                Status *
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="form-input"
                disabled={isSubmitting || isLoading}
              >
                {PlayingStatusSchema.options.map((status) => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() +
                      status.slice(1).replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="age" className="form-label">
                Age *
              </label>
              <input
                type="number"
                id="age"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                min="0"
                max="120"
                className={`form-input ${errors.age ? "error" : ""}`}
                disabled={isSubmitting || isLoading}
              />
              {errors.age && <span className="form-error">{errors.age}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="current_team" className="form-label">
              Current Team
            </label>
            <input
              type="text"
              id="current_team"
              name="current_team"
              value={formData.current_team ?? ""}
              onChange={handleInputChange}
              placeholder="e.g., Al Nassr"
              className="form-input"
              disabled={isSubmitting || isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="league" className="form-label">
              League
            </label>
            <input
              type="text"
              id="league"
              name="league"
              value={formData.league ?? ""}
              onChange={handleInputChange}
              placeholder="e.g., Saudi Pro League"
              className="form-input"
              disabled={isSubmitting || isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="market_value" className="form-label">
              Market Value (USD)
            </label>
            <input
              type="number"
              id="market_value"
              name="market_value"
              value={formData.market_value ?? ""}
              onChange={handleInputChange}
              min="0"
              placeholder="e.g., 50000000"
              className={`form-input ${errors.market_value ? "error" : ""}`}
              disabled={isSubmitting || isLoading}
            />
            {errors.market_value && (
              <span className="form-error">{errors.market_value}</span>
            )}
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={isSubmitting || isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting || isLoading}
            >
              {isSubmitting || isLoading ? (
                <>
                  <FontAwesomeIcon icon={faSpinner} className="spinner-icon" />
                  {isEditing ? "Updating..." : "Creating..."}
                </>
              ) : isEditing ? (
                "Update Player"
              ) : (
                "Add Player"
              )}
            </button>
          </div>
        </form>
      </div>
    </>
  );
};

export default PlayerFormModal;
