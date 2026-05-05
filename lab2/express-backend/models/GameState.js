const mongoose = require('mongoose');

const gameStateSchema = new mongoose.Schema({
  roomId: {
    type: String,
    required: [true, 'Room ID is required'],
    unique: true
  },
  players: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  status: {
    type: String,
    enum: ['waiting', 'playing', 'finished'],
    default: 'waiting'
  },
  moves: {
    type: Map,
    of: String
  }
});

module.exports = mongoose.model('GameState', gameStateSchema);