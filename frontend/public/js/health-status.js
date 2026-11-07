// Health status on the home page (spec 0001, AC-3..AC-5).
// Pure logic + one render function; DOM wiring lives in main.js.

export const MESSAGES = Object.freeze({
  checking: "Sistem durumu kontrol ediliyor…",
  running: "Sistem çalışıyor",
  error: "Sistem şu anda yanıt vermiyor. Lütfen daha sonra tekrar deneyin.",
});

// Resolves to "running" or "error"; never rejects.
export async function fetchHealthState(fetchFn) {
  try {
    const response = await fetchFn("/api/health", { headers: { Accept: "application/json" } });
    if (!response.ok) return "error";
    const body = await response.json();
    return body && body.status === "ok" ? "running" : "error";
  } catch {
    return "error";
  }
}

// Fixed messages only, written as text — server content is never rendered as HTML.
export function renderState(element, state) {
  element.textContent = MESSAGES[state];
  element.dataset.state = state;
}

export async function initHealthStatus(doc, fetchFn) {
  const element = doc.getElementById("health-status");
  renderState(element, "checking");
  const state = await fetchHealthState(fetchFn);
  renderState(element, state);
  return state;
}
