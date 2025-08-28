const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// Get all payment receivers
const getPaymentReceivers = async (req, res) => {
  try {
    const receivers = await prisma.paymentReceiverDetails.findMany({
      orderBy: {
        createdAt: 'desc'
      }
    });

    res.status(200).json({
      success: true,
      data: receivers
    });
  } catch (error) {
    console.error('Error fetching payment receivers:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch payment receivers',
      error: error.message
    });
  }
};

// Create payment receiver
const createPaymentReceiver = async (req, res) => {
  try {
    const { phoneNumber, accountNumber } = req.body;

    // Validate input
    if (!phoneNumber && !accountNumber) {
      return res.status(400).json({
        success: false,
        message: 'Either phone number or account number is required'
      });
    }

    const receiver = await prisma.paymentReceiverDetails.create({
      data: {
        phoneNumber,
        accountNumber
      }
    });

    res.status(201).json({
      success: true,
      message: 'Payment receiver created successfully',
      data: receiver
    });
  } catch (error) {
    console.error('Error creating payment receiver:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create payment receiver',
      error: error.message
    });
  }
};

const createPaymentSession = async (req, res) => {
  try {
    const { amount, phone_number, telegram_id, tx_ref } = req.body;
    console.log("req.body", req.body);
    
    if (!amount || !phone_number || !telegram_id || !tx_ref) {
      console.log("All fields are required");
      return res.status(400).json({
        success: false,
        message: 'All fields are required'
      });
    }

    // First check if the player exists
    const player = await prisma.player.findUnique({
      where: { telegramId: telegram_id.toString() }
    });

    if (!player) {
      return res.status(404).json({
        success: false,
        message: 'Player not found. Please register first.'
      });
    }

    const paymentSession = await prisma.paymentSession.create({
      data: {
        playerId: player.id, // Use the actual player ID from the database
        amount: parseFloat(amount),
        txRef: tx_ref,
        paymentMethod: "manual",
        status: "pending",
        expiresAt: new Date(Date.now() + 5 * 60 * 1000), // 5 minutes from now
        sessionData: {
          phoneNumber: phone_number,
          telegramId: telegram_id
        }
      }
    });

    console.log("paymentSession", paymentSession);
    res.status(201).json({
      success: true,
      message: 'Payment session created successfully',
      data: paymentSession
    });
  } catch (error) {
    console.error('Error creating payment session:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create payment session',
      error: error.message
    });
  }
};
    1
module.exports = {
  getPaymentReceivers,
  createPaymentReceiver,
  createPaymentSession
};
