const express = require('express');
const { getPaymentReceivers,
     createPaymentReceiver,
     createPaymentSession,
     createPaymentRequest,
     getPaymentSessions,
     getPaymentRequests,
     getPaymentSessionByTelegramId,
    getPaymentRequestByTelegramId,
     rejectWithdrawalRequest,
     approveWithdrawalRequest
    } = require('../controllers/payments');
const router = express.Router();

router.get('/receivers', getPaymentReceivers);
router.post('/receivers', createPaymentReceiver);
router.get('/payment-sessions', getPaymentSessions);
router.post('/payment-session', createPaymentSession);
router.get('/payment-session/:telegram_id', getPaymentSessionByTelegramId);

router.get('/payment-request', getPaymentRequests);
router.post('/payment-request', createPaymentRequest);
router.get('/payment-request/:telegram_id', getPaymentRequestByTelegramId);
router.post('/payment-request/reject/:id', rejectWithdrawalRequest);
router.post('/payment-request/approve/:id', approveWithdrawalRequest);

module.exports = router;
module.exports = router;
