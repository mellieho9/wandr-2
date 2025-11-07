/**
 * Frontend configuration
 * API base URL for Flask backend
 */

// Determine API base URL based on environment
const getApiBaseUrl = (): string => {
  // In production, the frontend is served from the same origin as the API
  // In development, you might need to point to a different port
  if (import.meta.env.DEV) {
    return "http://localhost:8080";
  }
  return ""; // Same origin in production
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  AUTH_LOGIN: `${API_BASE_URL}/auth/notion/login`,
  AUTH_CALLBACK: `${API_BASE_URL}/auth/notion/callback`,
  DATABASES_AVAILABLE: `${API_BASE_URL}/api/databases/available`,
  DATABASES_REGISTER: `${API_BASE_URL}/api/databases/register`,
  DATABASES_LIST: `${API_BASE_URL}/api/databases`,
  LINK_DATABASE_REGISTER: `${API_BASE_URL}/api/link-database/register`,
};
