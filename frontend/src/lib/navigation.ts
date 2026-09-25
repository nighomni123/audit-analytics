export type Screen =
  | "home"
  | "engagement"
  | "population"
  | "methodology"
  | "analysis"
  | "dashboard"
  | "risk"
  | "investigation"
  | "sample"
  | "workpapers"
  | "activity"
  | "audit-trail";

export interface RouteState {
  screen: Screen;
  params: URLSearchParams;
}

const screens = new Set<Screen>([
  "home",
  "engagement",
  "population",
  "methodology",
  "analysis",
  "dashboard",
  "risk",
  "investigation",
  "sample",
  "workpapers",
  "activity",
  "audit-trail",
]);

export function readRoute(): RouteState {
  const raw = window.location.hash.replace(/^#\/?/, "");
  const [path, query = ""] = raw.split("?", 2);
  const candidate = path || "home";
  const screen: Screen = screens.has(candidate as Screen) ? (candidate as Screen) : "home";
  return { screen, params: new URLSearchParams(query) };
}

export function navigate(screen: Screen, params: Record<string, string | number | null | undefined> = {}): void {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") query.set(key, String(value));
  });
  const suffix = query.toString();
  const next = `#/${screen}${suffix ? `?${suffix}` : ""}`;
  if (window.location.hash !== next) window.location.hash = next;
}
