const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const sendTelegramMessage = require('../helpers/sendTelegramMessage');

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


const createPaymentRequest = async (req, res) => {
  try {
    console.log("req.body", req.body);
    const { telegram_id, amount } = req.body;

    if (!telegram_id || !amount) {
      return res.status(400).json({
        success: false,
        message: 'telegram_id and amount are required'
      });
    }

 
    const player = await prisma.player.findUnique({
      where: { telegramId: telegram_id.toString() }
    });

    if (!player) {
      return res.status(404).json({
        success: false,
        message: 'Player not found. Please register first.'
      });
    }
    // Create payment request
    const paymentRequest = await prisma.paymentRequest.create({
      data: {
        playerId: player.id,
        amount: parseFloat(amount),
        status: 'pending'
      }
    });



    res.status(201).json({
      success: true,
      message: 'Payment request submitted successfully',
      data: paymentRequest
    });
  } catch (error) {
    console.error('Error creating payment request:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create payment request',
      error: error.message
    });
  }
};

const getPaymentSessions = async (req, res) => {    
    try {
       
      

        const paymentSessions = await prisma.paymentSession.findMany({
           
            include: {
                player: {
                    select: {
                        telegramId: true,
                        phoneNumber: true,
                        username: true
                    }
                }
            }
        });
        
        res.status(200).json({
            success: true,
            data: paymentSessions
        });
    }
    catch (error) {
        console.error('Error fetching payment sessions:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch payment sessions',
            error: error.message
        });
    }
};

const getPaymentRequests = async (req, res) => {
    try {
        const paymentRequests = await prisma.paymentRequest.findMany({
            include: {
                player: {
                    select: {
                        games:true,
                        telegramId: true,
                        phoneNumber: true,
                        username: true
                    }
                }
            }
        
            
        });
        
        
        res.status(200).json({
            success: true,
            data: paymentRequests
        });
    }
    catch (error) {
        console.error('Error fetching payment requests:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch payment requests',
            error: error.message
        });
    }
};

const getPaymentSessionByTelegramId = async (req, res) => {

    try {
        const { telegram_id } = req.params;
        
        // Validate telegram_id parameter
        if (!telegram_id) {
            return res.status(400).json({
                success: false,
                message: 'telegram_id parameter is required'
            });
        }
        
        // First find the player by telegram_id
        const player = await prisma.player.findUnique({
            where: { telegramId: telegram_id.toString() }
        });

        if (!player) {
            return res.status(404).json({
                success: false,
                message: 'Player not found'
            });
        }

        const paymentSession = []
        
        res.status(200).json({
            success: true,
            data: paymentSession
        });
    }
    catch (error) {
        console.error('Error fetching payment session:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch payment session',
            error: error.message
        });
    }
};

const getPaymentRequestByTelegramId = async (req, res) => {

    try {
        const { telegram_id } = req.params;
        
        // Validate telegram_id parameter
        if (!telegram_id) {
            return res.status(400).json({
                success: false,
                message: 'telegram_id parameter is required'
            });
        }
        
        // First find the player by telegram_id
        const player = await prisma.player.findUnique({
            where: { telegramId: telegram_id.toString() }
        });

        if (!player) {
            return res.status(404).json({
                success: false,
                message: 'Player not found'
            });
        }

        // Find the most recent payment request for this player
        const paymentRequest = await prisma.paymentRequest.findFirst({
            where: { 
                playerId: player.id 
            },
            orderBy: {
                createdAt: 'desc'
            },
            include: {
                player: {
                    select: {
                        telegramId: true,
                        phoneNumber: true,
                        username: true
                    }
                }
               
            }
        });

        if (!paymentRequest) {
            return res.status(404).json({
                success: false,
                message: 'No payment request found for this player'
            });
        }
        console.log("paymentRequest", paymentRequest);
        
        res.status(200).json({
            success: true,
            data: paymentRequest
        });
    }
    catch (error) {
        console.error('Error fetching payment request:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch payment request',
            error: error.message
        });
    }
};

const rejectWithdrawalRequest = async (req, res) => {
    try {
        const { id } = req.params;
        const paymentRequest = await prisma.paymentRequest.update({
            where: { id: parseInt(id) },
            data: { status: 'rejected' }
        });
        const player = await prisma.player.findUnique({
            where: { id: paymentRequest.playerId }
        });
        if (!player) {
            return res.status(404).json({
                success: false,
                message: 'Player not found'
            });
        }   
        player.balance += paymentRequest.amount;
        await prisma.player.update({
            where: { id: paymentRequest.playerId },
            data: { balance: player.balance }
        });
        // delete the payment request
        await prisma.paymentRequest.delete({
            where: { id: parseInt(id) }
        });

        // notfiy telegram user that the withdrawal request has been rejected
        const telegramId = player.telegramId;
        const message = `Your withdrawal request has been rejected. Your balance has been credited back to your account.`;
        await sendTelegramMessage(telegramId, message);
        res.status(200).json({
            success: true,
            message: 'Withdrawal request rejected successfully',
            data: paymentRequest
        });
    }
    catch (error) {
        console.error('Error rejecting withdrawal request:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to reject withdrawal request',
            error: error.message
        });
    }
};


const approveWithdrawalRequest = async (req, res) => {
    try {
        const { id } = req.params;
        const paymentRequest = await prisma.paymentRequest.update({
            where: { id: parseInt(id) },
            data: { status: 'approved' }
        });
        const player = await prisma.player.findUnique({
            where: { id: paymentRequest.playerId }
        });
        if (!player) {
            return res.status(404).json({
                success: false,
                message: 'Player not found'
            });
        }

        // deduct the amount from the player's balance
        player.balance -= paymentRequest.amount;
        
        await prisma.player.update({
            where: { id: paymentRequest.playerId },
            data: { balance: player.balance }
        });

        // notify telegram user that the withdrawal request has been approved
        const telegramId = player.telegramId;
        const message = `Your withdrawal request has been approved. Your balance has been debited from your account.`;
        await sendTelegramMessage(telegramId, message);

        res.status(200).json({
            success: true,
            message: 'Withdrawal request approved successfully',
            data: paymentRequest
        });
    }
    catch (error) {
        console.error('Error approving withdrawal request:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to approve withdrawal request',
            error: error.message
        });
    }
   
};




module.exports = {
  getPaymentReceivers,
  createPaymentReceiver,
  createPaymentSession,
  createPaymentRequest,
  getPaymentSessions,
  getPaymentRequests,
  getPaymentSessionByTelegramId,
  getPaymentRequestByTelegramId,
  rejectWithdrawalRequest,
  approveWithdrawalRequest
};
