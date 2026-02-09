import { useEffect, useState, useCallback } from "react";
import { createPortal } from "react-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faXmark,
  faEarthEurope,
  faCakeCandles,
} from "@fortawesome/free-solid-svg-icons";
import type { Player, TaskStatus } from "../../types";
import { scoutPlayer, getTaskStatus } from "../../services/api";
import { formatCurrency, getStatusColor, parseScoutReport } from "../../utils";
import "./ScoutReportModal.css";

interface ScoutReportModalProps {
  player: Player;
  onClose: () => void;
  onReportGenerated: () => void;
}

const STAGE_LABELS: Record<string, string> = {
  init: "Initializing AI Scout...",
  pending: "Queued for analysis...",
  running: "AI is analyzing player data...",
  completed: "Report ready!",
  failed: "Analysis failed",
};

const renderTextWithBold = (text: string) => {
  // Split on **bold** markers and render as <strong>
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  );
};

const ScoutReportModal = ({
  player,
  onClose,
  onReportGenerated,
}: ScoutReportModalProps) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const stableOnReportGenerated = useCallback(onReportGenerated, []);

  // Start scouting when modal opens
  useEffect(() => {
    const initiateScout = async () => {
      try {
        const response = await scoutPlayer(player.id);
        setTaskId(response.task_id);
        setIsPolling(true);
      } catch (err) {
        setError("Failed to initiate scouting. Please try again.");
        console.error(err);
      }
    };

    if (!player.scouting_report) {
      initiateScout();
    }
  }, [player.id, player.scouting_report]);

  // Poll for task status
  useEffect(() => {
    if (!taskId || !isPolling) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await getTaskStatus(taskId);
        setTaskStatus(status);

        if (status.status === "completed" || status.status === "failed") {
          setIsPolling(false);
          clearInterval(pollInterval);

          if (status.status === "completed") {
            setTimeout(() => {
              stableOnReportGenerated();
            }, 1000);
          }
        }
      } catch (err) {
        console.error("Error polling task status:", err);
        setError("Failed to fetch task status");
        setIsPolling(false);
        clearInterval(pollInterval);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [taskId, isPolling, stableOnReportGenerated]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const currentStage = !taskStatus
    ? "init"
    : taskStatus.status;

  const sections = player.scouting_report
    ? parseScoutReport(player.scouting_report)
    : [];

  const hasReport = !!player.scouting_report;
  const isComplete = taskStatus?.status === "completed";
  const isFailed = taskStatus?.status === "failed" || !!error;

  return createPortal(
    <div className="scout-backdrop" onClick={onClose}>
      <div
        className="scout-modal-container"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Gradient top bar */}
        <div className="scout-modal-accent" />

        {/* Close button */}
        <button
          className="scout-modal-close"
          onClick={onClose}
          aria-label="Close scout report"
        >
          <FontAwesomeIcon icon={faXmark} />
        </button>

        {/* Header */}
        <div className="scout-modal-header">
          <span className="scout-modal-tag">AI SCOUT REPORT</span>
        </div>

        {/* Player Banner */}
        <div className="scout-player-banner">
          <div className="scout-player-avatar">
            {player.full_name.charAt(0)}
          </div>
          <div className="scout-player-info">
            <h2 className="scout-player-name">{player.full_name}</h2>
            <div className="scout-player-meta">
              <span className="scout-meta-item">
                <FontAwesomeIcon icon={faEarthEurope} />
                {player.country}
              </span>
              <span className="scout-meta-item">
                <FontAwesomeIcon icon={faCakeCandles} />
                {player.age} yrs
              </span>
              <span className="scout-meta-item">
                {player.current_team || "Free Agent"}
              </span>
              {player.league && (
                <span className="scout-meta-item">{player.league}</span>
              )}
            </div>
            <div className="scout-player-badges">
              <span
                className={`scout-status-badge ${getStatusColor(player.status)}`}
              >
                {player.status.replace("_", " ")}
              </span>
              {player.market_value != null && (
                <span className="scout-value-badge">
                  {formatCurrency(player.market_value)}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Content area */}
        <div className="scout-modal-body">
          {hasReport ? (
            <div className="scout-report-sections">
              {sections.map((section, i) => (
                <div
                  className="scout-section"
                  key={i}
                  style={{ animationDelay: `${i * 0.08}s` }}
                >
                  <h4 className="scout-section-title">{section.title}</h4>
                  <p className="scout-section-content">
                    {renderTextWithBold(section.content)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="scout-loading-area">
              <div className="scout-spinner-ring">
                <div
                  className={`scout-spinner-circle ${isComplete ? "complete" : ""} ${isFailed ? "failed" : ""}`}
                />
              </div>
              <div className="scout-loading-stages">
                {Object.entries(STAGE_LABELS).map(([key, label]) => {
                  const stageOrder = [
                    "init",
                    "pending",
                    "running",
                    "completed",
                    "failed",
                  ];
                  const currentIdx = stageOrder.indexOf(currentStage);
                  const keyIdx = stageOrder.indexOf(key);

                  // Don't show 'failed' stage if not failed
                  if (key === "failed" && !isFailed) return null;
                  // Don't show 'completed' stage while still in progress
                  if (key === "completed" && !isComplete && !isFailed)
                    return null;

                  let stageClass = "scout-stage";
                  if (keyIdx < currentIdx) stageClass += " done";
                  else if (keyIdx === currentIdx) stageClass += " active";

                  return (
                    <div className={stageClass} key={key}>
                      <span className="scout-stage-dot" />
                      <span className="scout-stage-label">{label}</span>
                    </div>
                  );
                })}
              </div>
              {error && <p className="scout-error-msg">{error}</p>}
              {taskStatus?.error && (
                <p className="scout-error-msg">{taskStatus.error}</p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="scout-modal-footer">
          <button className="scout-close-btn" onClick={onClose}>
            {isComplete || hasReport ? "Close" : "Cancel"}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ScoutReportModal;
