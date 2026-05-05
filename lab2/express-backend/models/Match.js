const mongoose = require('mongoose');

const matchSchema = new mongoose.Schema({
  player1: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Player 1 is required']
  },
  player2: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Player 2 is required']
  },
  winner: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null
  },
  moves: {
    p1Move: {
      type: String,
      enum: ['rock', 'paper', 'scissors']
    },
    p2Move: {
      type: String,
      enum: ['rock', 'paper', 'scissors']
    }
  },
  playedAt: {
    type: Date,
    default: Date.now,
    index: -1
  }
});

matchSchema.index({ player1: 1, playedAt: -1 });
matchSchema.index({ player2: 1, playedAt: -1 });

module.exports = mongoose.model('Match', matchSchema);