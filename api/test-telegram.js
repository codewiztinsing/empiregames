require('dotenv').config();
const { testTelegramConnection } = require('./helpers/sendTelegramMessage');

async function testConnection() {
    console.log('Testing Telegram connection...');
    console.log('Bot Token configured:', !!process.env.TELEGRAM_BOT_TOKEN);
    
    try {
        const result = await testTelegramConnection();
        if (result) {
            console.log('✅ Telegram connection test successful!');
        } else {
            console.log('❌ Telegram connection test failed!');
        }
    } catch (error) {
        console.error('Error during connection test:', error.message);
    }
}

testConnection();


