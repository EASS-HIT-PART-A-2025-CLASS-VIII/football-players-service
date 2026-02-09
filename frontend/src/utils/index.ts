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

export interface ReportSection {
  title: string;
  content: string;
}

export const parseScoutReport = (text: string): ReportSection[] => {
  if (!text || !text.trim()) return [];

  // Split on **Header:** or **Header** patterns
  const sectionRegex = /\*\*([^*]+?)(?::)?\*\*\s*/g;
  const sections: ReportSection[] = [];
  let lastIndex = 0;
  let lastTitle: string | null = null;
  let match: RegExpExecArray | null;

  while ((match = sectionRegex.exec(text)) !== null) {
    // Capture content before this header (belongs to previous section or preamble)
    if (lastTitle !== null) {
      const content = text.slice(lastIndex, match.index).trim();
      if (content) {
        sections.push({ title: lastTitle, content });
      }
    } else {
      // Any text before the first header becomes an "Overview"
      const preamble = text.slice(0, match.index).trim();
      if (preamble) {
        sections.push({ title: "Overview", content: preamble });
      }
    }

    lastTitle = match[1].trim();
    lastIndex = match.index + match[0].length;
  }

  // Capture the last section
  if (lastTitle !== null) {
    const content = text.slice(lastIndex).trim();
    if (content) {
      sections.push({ title: lastTitle, content });
    }
  }

  // Fallback: no headers found — wrap entire text as "Overview"
  if (sections.length === 0 && text.trim()) {
    sections.push({ title: "Overview", content: text.trim() });
  }

  return sections;
};
