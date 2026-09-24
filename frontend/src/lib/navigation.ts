export type Screen = "engagement" | "population" | "dashboard" | "investigation";

export interface RouteState {
  screen: Screen;
  params: URLSearchParams;
}

const screens = new Set<Screen>(["engagement", "population", "dashboard", "investigation"]);

export function readRoute(): RouteState {
  const raw = window.location.hash.replace(/^#\/?/, "");
  const [path, query = ""] = raw.split("?", 2);
  const screen = screens.has(path as Screen) ? (path as Screen) : "engagement";
  return { screen, params: new URLSearchParams(query) };
}

export function navigate(screen: Screen, params: Record<string, string | number | null | undefined> = {}): void {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") query.set(key, String(value));
  });
  const suffix = query.toString();
  window.location.hash = `#/${screen}${suffix ? `?${suffix}` : ""}`;
}
