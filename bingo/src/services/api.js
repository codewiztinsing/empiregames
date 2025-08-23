import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

//14603570
// Habtamu Hailemichael Belew
// Example endpoints
export const getUsers = () => api.get("/users");
export const getGames = () => api.get("/games");
export const getDashboardStats = () => api.get("/dashboard/stats");
export const getDashboardRecentStats = (timeRange) => api.get(`/dashboard/stats/recent?timeRange=${timeRange}`);
export const createUser = (data) => api.post("/users", data);
export const getUser = (telegramId) => api.get(`/users/${telegramId}`);
export const getAllUsers = () => api.get("/users");
export const updateUser = (telegramId, data) => api.put(`/users/${telegramId}`, data);

export default api;
