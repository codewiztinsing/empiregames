const express = require('express');
const { getPaymentReceivers, createPaymentReceiver, createPaymentSession } = require('../controllers/payments');
const router = express.Router();

router.get('/receivers', getPaymentReceivers);
router.post('/receivers', createPaymentReceiver);
router.post('/payment-session', createPaymentSession);
module.exports = router;
module.exports = router;
