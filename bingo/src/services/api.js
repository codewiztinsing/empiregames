import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
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
export const deleteApiPromotion = (id) => api.delete(`/promotions/${id}`);
export const createApiPromotion = (data) => api.post("/promotions", data);
export const createUser = (data) => api.post("/users", data);
export const createGame = (data) => api.post("/games", data);
export const getUser = (telegramId) => api.get(`/users/${telegramId}`);
export const getAllUsers = () => api.get("/users");
export const updateUser = (telegramId, data) => api.put(`/users/${telegramId}`, data);
export const deleteUser = (telegramId) => api.delete(`/users/${telegramId}`);
export const getWithdrawalRequests = () => api.get(`/payments/payment-request`);
export const getAutomaticDeposit = () => api.get(`/payments/payment-sessions`);
export const getWithdrawalRequestsByTelegramId = (telegramId) => api.get(`/payments/payment-request/${telegramId}`);
export const getPaymentSessionsByTelegramId = (telegramId) => api.get(`/payments/payment-session/${telegramId}`);
export const rejectWithdrawalRequest = (id) => api.post(`/payments/payment-request/reject/${id}`);
export const approveWithdrawalRequest = (id) => api.post(`/payments/payment-request/approve/${id}`);





export const login = (data) => api.post("/auth/login", data);
export const logout = () => api.post("/auth/logout");

export default api;
