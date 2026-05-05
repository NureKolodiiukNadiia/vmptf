const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: [true, 'Username is required'],
    unique: true,
    index: true,
    trim: true
  },
  wins: {
    type: Number,
    default: 0
  },
  losses: {
    type: Number,
    default: 0
  },
  draws: {
    type: Number,
    default: 0
  },
  score: {
    type: Number,
    default: 0,
    index: -1
  }
});

userSchema.pre('save', function(next) {
  this.score = this.wins * 3 + this.draws * 1;
  next();
});

module.exports = mongoose.model('User', userSchema);

