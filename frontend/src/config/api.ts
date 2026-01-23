/**
 * API configuration with endpoints, base URLs, and request/response settings.
 */

/**
 * API base URL from environment or default.
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * API version prefix.
 */
export const API_VERSION = "/api/v1";

/**
 * Full API base URL with version.
 */
export const API_URL = `${API_BASE_URL}${API_VERSION}`;

/**
 * Default request timeout in milliseconds.
 */
export const DEFAULT_TIMEOUT = 30000; // 30 seconds

/**
 * Default retry configuration.
 */
export const DEFAULT_RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryOn: [408, 429, 500, 502, 503, 504], // HTTP status codes to retry
};

/**
 * API endpoints configuration.
 */
export const API_ENDPOINTS = {
  // Common endpoints
  common: {
    health: "/common/health",
    version: "/common/version",
    status: "/common/status",
    info: "/common/info",
  },
  // Storage endpoints
  storage: {
    upload: "/storage/upload",
    download: (id: number) => `/storage/download/${id}`,
    delete: (id: number) => `/storage/${id}`,
    list: "/storage/list",
    url: (id: number) => `/storage/${id}/url`,
  },
  // Graph endpoints (placeholder)
  graph: {
    base: "/graph",
  },
  // Validator endpoints (placeholder)
  validator: {
    base: "/validator",
  },
} as const;

/**
 * Get full API endpoint URL.
 */
export function getApiUrl(endpoint: string): string {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;
  return `${API_URL}/${cleanEndpoint}`;
}

