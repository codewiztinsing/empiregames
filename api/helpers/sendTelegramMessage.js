const axios = require('axios');

// Create a custom axios instance with better timeout and retry configuration
const telegramAxios = axios.create({
    timeout: 15000, // 15 second timeout
    maxRedirects: 3,
    validateStatus: function (status) {
        return status >= 200 && status < 300; // Accept only 2xx status codes
    }
});

// send telegram message to a user with timeout and retry logic
const sendTelegramMessage = async (telegramId, message, retries = 2) => {
    try {
        const botToken = process.env.TELEGRAM_BOT_TOKEN;
        if (!botToken) {
            console.warn('TELEGRAM_BOT_TOKEN not configured, skipping message');
            return null;
        }

        if (!telegramId) {
            console.warn('No telegram ID provided, skipping message');
            return null;
        }

        const telegramApiUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
        
        const response = await telegramAxios.post(telegramApiUrl, {
            chat_id: telegramId,
            text: message,
            parse_mode: 'HTML'
        }, {
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'EmpireGames-Bot/1.0'
            }
        });
        
        console.log('Telegram message sent successfully to:', telegramId);
        return response.data;
    } catch (error) {
        console.error('Error sending telegram message:', error.message);
        
        // If we have retries left and it's a timeout/network error, retry
        if (retries > 0 && (error.code === 'ETIMEDOUT' || error.code === 'ECONNRESET' || error.code === 'ENOTFOUND' || error.code === 'ECONNABORTED')) {
            console.log(`Retrying telegram message (${retries} attempts left)...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries))); // Exponential backoff
            return sendTelegramMessage(telegramId, message, retries - 1);
        }
        
        // Log the error but don't throw it to prevent breaking the main operation
        console.warn(`Failed to send telegram message to ${telegramId} after all retries:`, error.message);
        return null;
    }
};

module.exports = sendTelegramMessage;
