import type { PlayingStatus } from "../types";

export const formatCurrency = (value: number | null | undefined) => {
  if (!value) return "N/A";
  return `$${(value / 1000000).toFixed(1)}M`;
};

export const getStatusColor = (status: PlayingStatus): string => {
  const colorMap: Record<PlayingStatus, string> = {
    active: "status-active",
    retired: "status-retired",
    free_agent: "status-free",
  };
  return colorMap[status];
};
