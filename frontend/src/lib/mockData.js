export const MOCK_HISTORY = [
  { id: "1", site: "shopmore.io", date: "2026-08-29", score: 41, risk: "high" },
  { id: "2", site: "newsdaily.com", date: "2026-08-22", score: 68, risk: "medium" },
  { id: "3", site: "cloudnotes.app", date: "2026-08-14", score: 88, risk: "low" },
];

export const MOCK_REPORT = {
  site: "shopmore.io",
  scannedAt: "Aug 29, 2026 · 14:02",
  score: 41,
  verdict: "High risk",
  categoryScores: {
    dataSharing: 22,
    retention: 38,
    userControl: 45,
    transparency: 61,
  },
  compareAverage: 64,
  summary:
    "This site collects broad personal data, shares it with third-party advertisers by default, and does not offer a clear way to delete your account or data. Cookie consent is pre-checked rather than opt-in.",
  clauses: [
    {
      level: "high",
      title: "Sells data to third parties",
      detail: "Shares or sells information with marketing partners.",
      source:
        "\"We may share, license, or sell information we collect to affiliates and marketing partners for their own promotional purposes.\" — Privacy Policy, Section 4.2",
      category: "Data sharing",
    },
    {
      level: "high",
      title: "No deletion option",
      detail: "No process described for users to request account or data deletion.",
      source:
        "The policy describes account deactivation but does not mention a data deletion or erasure request process anywhere in its text.",
      category: "User control",
    },
    {
      level: "medium",
      title: "Indefinite data retention",
      detail: "Data is kept with no fixed retention period.",
      source: "\"We retain your information for as long as necessary to fulfill business purposes.\" — Section 6.1",
      category: "Retention",
    },
    {
      level: "medium",
      title: "Broad location tracking",
      detail: "Precise location is collected even when the app is closed.",
      source: "\"With your permission, we may collect precise location data, including when the app is running in the background.\" — Section 3.4",
      category: "Data collection",
    },
    {
      level: "low",
      title: "Clear opt-out for email",
      detail: "Marketing emails include a working unsubscribe link.",
      source: "\"You may opt out of promotional emails at any time using the unsubscribe link included in each message.\" — Section 8.1",
      category: "User control",
    },
  ],
  trackers: [
    { name: "DoubleClick", type: "Advertising", count: 3 },
    { name: "Meta Pixel", type: "Advertising", count: 2 },
    { name: "Hotjar", type: "Analytics", count: 1 },
    { name: "Google Analytics", type: "Analytics", count: 4 },
  ],
  permissions: [
    { name: "Precise location", risk: "high" },
    { name: "Camera", risk: "low" },
    { name: "Contacts", risk: "medium" },
    { name: "Microphone", risk: "low" },
  ],
  recommendations: [
    "Look for a data deletion request form, or email the site to request one directly.",
    "Turn off precise location permissions for this site in your device settings.",
    "Use a tracker-blocking browser extension before continuing to shop here.",
  ],
};

export const EXAMPLE_SITES = ["https://nytimes.com", "https://spotify.com", "https://github.com"];

export function riskColor(level) {
  if (level === "high") return "#B23A2E";
  if (level === "medium") return "#B8862E";
  return "#3F6B4A";
}

export function verdictFor(score) {
  if (score >= 70) return "Low risk";
  if (score >= 45) return "Caution";
  return "High risk";
}

const severityRank = { high: 0, medium: 1, low: 2 };
export function sortBySeverity(clauses) {
  return [...clauses].sort((a, b) => severityRank[a.level] - severityRank[b.level]);
}
