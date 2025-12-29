import axios from "axios";

// ⚠️ CONFIGURACIÓN NGROK BACKEND
// Cuando uses ngrok, cierra el túnel del frontend, abre uno para el backend (puerto 8000),
// y pon esa URL aquí:
const NGROK_BACKEND_URL = 'https://361f3d7f7c0d.ngrok-free.app'; // Ejemplo: 'https://abc123.ngrok-free.app'

// Dynamically determine the API base URL
function getApiBaseUrl() {
  // Check if we have an environment variable set (for production)
  if (import.meta.env.VITE_API_URL) {
    return `${import.meta.env.VITE_API_URL}/api/`;
  }

  const hostname = window.location.hostname;

  // If we're on localhost, use localhost API
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/';
  }

  // PRODUCTION / NGROK / NETWORK:
  // Use relative path so it works everywhere automatically
  // (Frontend served by Django or Nginx on same domain)
  return '/api/';
}

// Utility function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrfToken = getCookie("csrftoken");
const API_BASE_URL = getApiBaseUrl();

console.log("API Base URL:", API_BASE_URL);

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "X-CSRFToken": csrfToken,
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true", // Bypass ngrok warning page for API calls
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    const excludedPaths = [
      "/profiles/login/",
      "/profiles/register/",
      "/auth/login/",
      "/auth/registration/",
      "/auth/google/",
      "/auth/facebook/"
    ];
    const isExcluded = excludedPaths.some(path => config.url.includes(path));

    if (token && !isExcluded) {
      console.log(`Sending Token to ${config.url}:`, token.substring(0, 10) + "...");
      // Check if it's a JWT (usually long with dots) or a simple Token (40 chars usually)
      if (token.length === 40 && !token.includes('.')) {
        config.headers.Authorization = `Token ${token}`;
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors globally
    if (error.response && error.response.status === 401) {
      console.warn("⚠️ 401 Unauthorized detected - Logging out...");

      // Avoid loops if already on auth page
      if (window.location.pathname.includes('/auth') || window.location.pathname === '/') {
        // return Promise.reject(error); 
      }

      // Clear storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Redirect to Auth
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Export the base URL for use in other files
export const apiBaseUrl = API_BASE_URL;
export default axiosInstance;
