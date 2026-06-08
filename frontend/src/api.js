const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");

async function parseError(res) {
  if (res.status === 504) {
    return "Request timed out — investigation takes ~30s. Use Vercel Pro or Cloud Run.";
  }
  if (res.status === 404) {
    return "API not found — check Vercel backend routePrefix is /api and env vars are set.";
  }
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg || d).join(", ");
    if (body.message) return body.message;
  } catch {
    /* ignore */
  }
  return `Request failed (HTTP ${res.status})`;
}

export async function apiRequest(path, options = {}) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE}${normalized}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}

export async function checkBackend() {
  try {
    const health = await apiRequest("/health");
    return { online: true, health };
  } catch (err) {
    return { online: false, error: err.message };
  }
}
