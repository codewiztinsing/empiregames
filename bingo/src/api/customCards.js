import config from '../config/api';
import apiClient from '../services/apiClient';

const API_BASE_URL = config.API_BASE_URL;

// Custom Cards API functions
export const customCardsAPI = {
  // Get all custom cards for a user
  async getUserCustomCards(telegramId) {
    try {
      const response = await apiClient.get(`game/custom-cards/?telegram_id=${telegramId}`);
      const data = response.data;
      return data.results || data.cards || data || [];
    } catch (error) {
      console.error('Error fetching user custom cards:', error);
      // Return empty array for development when server is not available
      console.log('Returning empty array for development');
      return [];
    }
  },

  // Get user's default custom card
  async getUserDefaultCard(telegramId) {
    try {
      const response = await apiClient.get(`game/custom-cards/default/?telegram_id=${telegramId}`);
      const data = response.data;
      return data.card || data;
    } catch (error) {
      console.error('Error fetching user default card:', error);
      // Return null for development when server is not available
      console.log('Returning null for development');
      return null;
    }
  },

  // Create a new custom card
  async createCustomCard(telegramId, cardData) {
    try {
      console.log('🆕 [API] Creating custom card:', { telegramId, cardData });
      
      const response = await apiClient.post(`game/custom-cards/create/`, {
        telegram_id: telegramId,
        ...cardData
      });
      
      console.log('✅ [API] Create card response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ [API] Error creating custom card:', error);
      console.error('❌ [API] Create card error details:', {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data,
        config: error.config,
        validationErrors: error.response?.data?.errors || error.response?.data?.error || 'No validation details'
      });
      throw error;
    }
  },

  // Update an existing custom card
  async updateCustomCard(cardId, cardData) {
    try {
      console.log('🔄 [API] Updating custom card:', { cardId, cardData });
      
      const response = await apiClient.put(`game/custom-cards/${cardId}/`, cardData);
      
      console.log('✅ [API] Update card response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ [API] Error updating custom card:', error);
      console.error('❌ [API] Update card error details:', {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data,
        config: error.config
      });
      throw error;
    }
  },

  // Delete a custom card
  async deleteCustomCard(cardId) {
    try {
      await apiClient.delete(`game/custom-cards/${cardId}/`);
      return true;
    } catch (error) {
      console.error('Error deleting custom card:', error);
      throw error;
    }
  },

  // Set a card as default
  async setDefaultCard(cardId) {
    try {
      const response = await apiClient.post(`game/custom-cards/${cardId}/set-default/`);
      return response.data;
    } catch (error) {
      console.error('Error setting default card:', error);
      throw error;
    }
  },

  // Generate a random card
  async generateRandomCard(telegramId) {
    try {
      const response = await apiClient.get(`game/custom-cards/generate-random-card/?telegram_id=${telegramId}`);
      return response.data;
    } catch (error) {
      console.error('Error generating random card:', error);
      throw error;
    }
  }
};

export default customCardsAPI;
