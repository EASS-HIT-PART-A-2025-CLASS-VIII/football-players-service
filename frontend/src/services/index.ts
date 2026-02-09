import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_LOCATION,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add JWT token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Handle 401 errors (expired/invalid token)
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const requestUrl = error.config?.url || "";

      // Don't redirect on login attempts - let the modal handle the error
      if (requestUrl === "/token") {
        return Promise.reject(error);
      }

      // Token expired or invalid on protected routes - clear and redirect
      localStorage.removeItem("access_token");
      window.location.href = "/";
    }
    return Promise.reject(error);
  },
);
