import { useState, useEffect, useCallback } from "react";
import type { PlayerFilters as FilterType, FilterOptions } from "../../types";
import "./PlayerFilters.css";

interface PlayerFiltersProps {
  filters: FilterType;
  filterOptions?: FilterOptions;
  onFiltersChange: (filters: FilterType) => void;
  onClear: () => void;
  onClearField?: (field: keyof FilterType) => void;
  disabled?: boolean;
}

interface ClearButtonProps {
  field: keyof FilterType;
  hasValue: boolean;
  onClear: (field: keyof FilterType) => void;
  disabled?: boolean;
}

const ClearButton = ({
  field,
  hasValue,
  onClear,
  disabled,
}: ClearButtonProps) => {
  if (!hasValue) return null;

  return (
    <button
      type="button"
      className="filter-clear-btn"
      onClick={() => onClear(field)}
      disabled={disabled}
      title={`Clear ${field}`}
    >
      ×
    </button>
  );
};

const PlayerFilters = ({
  filters,
  filterOptions,
  onFiltersChange,
  onClear,
  onClearField,
  disabled = false,
}: PlayerFiltersProps) => {
  // Local state for debounced name search
  const [nameInput, setNameInput] = useState(filters.name || "");
  const [minPriceInput, setMinPriceInput] = useState(
    filters.minPrice?.toString() || "",
  );
  const [maxPriceInput, setMaxPriceInput] = useState(
    filters.maxPrice?.toString() || "",
  );

  // Debounce name search
  useEffect(() => {
    const timer = setTimeout(() => {
      if ((nameInput || undefined) !== filters.name) {
        onFiltersChange({ ...filters, name: nameInput || undefined });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [nameInput, filters, onFiltersChange]);

  // Debounce price inputs
  useEffect(() => {
    const timer = setTimeout(() => {
      const minPrice = minPriceInput ? parseInt(minPriceInput, 10) : undefined;
      const maxPrice = maxPriceInput ? parseInt(maxPriceInput, 10) : undefined;

      if (minPrice !== filters.minPrice || maxPrice !== filters.maxPrice) {
        onFiltersChange({ ...filters, minPrice, maxPrice });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [minPriceInput, maxPriceInput, filters, onFiltersChange]);

  const handleClear = () => {
    setNameInput("");
    setMinPriceInput("");
    setMaxPriceInput("");
    onClear();
  };

  const handleClearField = (field: keyof FilterType) => {
    if (field === "name") {
      setNameInput("");
    } else if (field === "minPrice") {
      setMinPriceInput("");
    } else if (field === "maxPrice") {
      setMaxPriceInput("");
    }

    if (onClearField) {
      onClearField(field);
    } else {
      // Fallback to manual clearing if onClearField is not provided
      const newFilters = { ...filters };
      delete newFilters[field];
      onFiltersChange(newFilters);
    }
  };

  const handleFilterChange = useCallback(
    (key: keyof FilterType, value: string | undefined) => {
      onFiltersChange({ ...filters, [key]: value || undefined });
    },
    [filters, onFiltersChange],
  );

  // Count active filters (excluding name as it's always visible)
  const activeFilterCount = [
    filters.minPrice,
    filters.maxPrice,
    filters.country,
    filters.club,
    filters.league,
    filters.status,
  ].filter((v) => v !== undefined && v !== null).length;

  return (
    <div className="player-filters">
      <div className="filters-container">
        {/* Search Bar */}
        <div
          className={`filter-group search-group ${nameInput ? "has-value" : ""}`}
        >
          <label htmlFor="search-name">Search Player</label>
          <input
            id="search-name"
            type="text"
            placeholder="Search by name..."
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            disabled={disabled}
            className="search-input"
          />
          <ClearButton
            field="name"
            hasValue={!!nameInput}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* Country Filter */}
        <div className={`filter-group ${filters.country ? "has-value" : ""}`}>
          <label htmlFor="country">Country</label>
          <select
            id="country"
            value={filters.country || ""}
            onChange={(e) => handleFilterChange("country", e.target.value)}
            disabled={disabled || !filterOptions?.countries}
          >
            <option value="">All Countries</option>
            {(filterOptions?.countries ?? []).map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
          <ClearButton
            field="country"
            hasValue={!!filters.country}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* Club Filter */}
        <div className={`filter-group ${filters.club ? "has-value" : ""}`}>
          <label htmlFor="club">Club</label>
          <select
            id="club"
            value={filters.club || ""}
            onChange={(e) => handleFilterChange("club", e.target.value)}
            disabled={disabled || !filterOptions?.clubs}
          >
            <option value="">All Clubs</option>
            {(filterOptions?.clubs ?? []).map((club) => (
              <option key={club} value={club}>
                {club}
              </option>
            ))}
          </select>
          <ClearButton
            field="club"
            hasValue={!!filters.club}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* League Filter */}
        <div className={`filter-group ${filters.league ? "has-value" : ""}`}>
          <label htmlFor="league">League</label>
          <select
            id="league"
            value={filters.league || ""}
            onChange={(e) => handleFilterChange("league", e.target.value)}
            disabled={disabled || !filterOptions?.leagues}
          >
            <option value="">All Leagues</option>
            {(filterOptions?.leagues ?? []).map((league) => (
              <option key={league} value={league}>
                {league}
              </option>
            ))}
          </select>
          <ClearButton
            field="league"
            hasValue={!!filters.league}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* Status Filter */}
        <div className={`filter-group ${filters.status ? "has-value" : ""}`}>
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={filters.status || ""}
            onChange={(e) => handleFilterChange("status", e.target.value)}
            disabled={disabled || !filterOptions?.statuses}
          >
            <option value="">All Statuses</option>
            {(filterOptions?.statuses ?? []).map((status) => (
              <option key={status} value={status}>
                {status.replace("_", " ")}
              </option>
            ))}
          </select>
          <ClearButton
            field="status"
            hasValue={!!filters.status}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* Price Range */}
        <div
          className={`filter-group price-group ${minPriceInput ? "has-value" : ""}`}
        >
          <label htmlFor="min-price">Min Price</label>
          <input
            id="min-price"
            type="number"
            placeholder="Min"
            value={minPriceInput}
            onChange={(e) => setMinPriceInput(e.target.value)}
            disabled={disabled}
            min="0"
          />
          <ClearButton
            field="minPrice"
            hasValue={!!minPriceInput}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        <div
          className={`filter-group price-group ${maxPriceInput ? "has-value" : ""}`}
        >
          <label htmlFor="max-price">Max Price</label>
          <input
            id="max-price"
            type="number"
            placeholder="Max"
            value={maxPriceInput}
            onChange={(e) => setMaxPriceInput(e.target.value)}
            disabled={disabled}
            min="0"
          />
          <ClearButton
            field="maxPrice"
            hasValue={!!maxPriceInput}
            onClear={handleClearField}
            disabled={disabled}
          />
        </div>

        {/* Clear Button */}
        <div className="filter-actions">
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled || activeFilterCount === 0}
            className="clear-button"
          >
            Clear All
            {activeFilterCount > 0 && (
              <span className="filter-badge">{activeFilterCount}</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PlayerFilters;
