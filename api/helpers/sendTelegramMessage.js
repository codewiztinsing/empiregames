const axios = require('axios');

// Create a custom axios instance with better timeout and retry configuration
const telegramAxios = axios.create({
    timeout: 15000, // 15 second timeout
    maxRedirects: 3,
    validateStatus: function (status) {
        return status >= 200 && status < 300; // Accept only 2xx status codes
    },
    // Add connection pooling and keep-alive
    httpAgent: new (require('http').Agent)({
        keepAlive: true,
        keepAliveMsecs: 1000,
        maxSockets: 10,
        maxFreeSockets: 5
    }),
    httpsAgent: new (require('https').Agent)({
        keepAlive: true,
        keepAliveMsecs: 1000,
        maxSockets: 10,
        maxFreeSockets: 5
    })
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

        console.log(`Attempting to send Telegram message to ${telegramId}: ${message.substring(0, 50)}...`);
        
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
        
        // Categorize errors for better retry logic
        const isRetryableError = error.code === 'ETIMEDOUT' || 
                                error.code === 'ECONNRESET' || 
                                error.code === 'ENOTFOUND' || 
                                error.code === 'ECONNABORTED' ||
                                error.code === 'ENETUNREACH' ||
                                error.code === 'EHOSTUNREACH';
        
        // If we have retries left and it's a retryable error, retry
        if (retries > 0 && isRetryableError) {
            console.log(`Retrying telegram message (${retries} attempts left)...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries))); // Exponential backoff
            return sendTelegramMessage(telegramId, message, retries - 1);
        }
        
        // Log the error but don't throw it to prevent breaking the main operation
        console.warn(`Failed to send telegram message to ${telegramId} after all retries:`, error.message);
        return null;
    }
};

// Test function to verify Telegram connectivity
const testTelegramConnection = async () => {
    try {
        const botToken = process.env.TELEGRAM_BOT_TOKEN;
        if (!botToken) {
            console.warn('TELEGRAM_BOT_TOKEN not configured');
            return false;
        }

        const response = await telegramAxios.get(`https://api.telegram.org/bot${botToken}/getMe`, {
            timeout: 10000
        });
        
        console.log('Telegram connection test successful:', response.data);
        return true;
    } catch (error) {
        console.error('Telegram connection test failed:', error.message);
        return false;
    }
};

module.exports = { sendTelegramMessage, testTelegramConnection };
