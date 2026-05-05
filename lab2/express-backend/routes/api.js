const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

router.post('/auth/login', userController.login);
router.get('/users/:userId', userController.getUser);
router.put('/users/:userId', userController.updateUser);
router.get('/leaderboard', userController.getLeaderboard);
router.get('/stats/global', userController.getStats);
router.get('/matches/user/:userId', userController.getMatchHistory);
router.get('/matches/:matchId', userController.getMatch);

module.exports = router;