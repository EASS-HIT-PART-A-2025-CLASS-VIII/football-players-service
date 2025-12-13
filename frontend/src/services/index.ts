import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_LOCATION,
  headers: {
    "Content-Type": "application/json",
  },
});
