import config from '../config/api';

const API_BASE_URL = config.API_BASE_URL;

// Custom Cards API functions
export const customCardsAPI = {
  // Get all custom cards for a user
  async getUserCustomCards(telegramId) {
    try {
      const response = await fetch(`${API_BASE_URL}game/custom-cards/?telegram_id=${telegramId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          // No custom cards found, return empty array
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
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
      const response = await fetch(`${API_BASE_URL}game/custom-cards/default/?telegram_id=${telegramId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          // No default card found
          return null;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
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
      const response = await fetch(`${API_BASE_URL}game/custom-cards/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_id: telegramId,
          ...cardData
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating custom card:', error);
      throw error;
    }
  },

  // Update an existing custom card
  async updateCustomCard(cardId, cardData) {
    try {
      const response = await fetch(`${API_BASE_URL}game/custom-cards/${cardId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cardData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error updating custom card:', error);
      throw error;
    }
  },

  // Delete a custom card
  async deleteCustomCard(cardId) {
    try {
      const response = await fetch(`${API_BASE_URL}game/custom-cards/${cardId}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting custom card:', error);
      throw error;
    }
  },

  // Set a card as default
  async setDefaultCard(cardId) {
    try {
      const response = await fetch(`${API_BASE_URL}game/custom-cards/${cardId}/set-default/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error setting default card:', error);
      throw error;
    }
  },

  // Generate a random card
  async generateRandomCard(telegramId) {
    try {
      const response = await fetch(`${API_BASE_URL}game/custom-cards/generate-random/?telegram_id=${telegramId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error generating random card:', error);
      throw error;
    }
  }
};

export default customCardsAPI;
