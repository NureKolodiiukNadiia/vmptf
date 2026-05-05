const User = require('../models/User');
const Match = require('../models/Match');

exports.login = async (req, res) => {
  try {
    const { username } = req.body;

    if (!username) {
      return res.status(400).json({ error: 'Username is required' });
    }

    console.log(username);
    let user = await User.findOne({ username });

    if (!user) {
      user = await User.create({ username });
    }

    res.status(201).json({
      userId: user._id,
      username: user.username
    });
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Username already exists' });
    }
    if (error.name === 'ValidationError') {
      return res.status(400).json({ error: error.message });
    }
    res.status(500).json({ error: error.message });
  }
};

exports.getUser = async (req, res) => {
  try {
    const { userId } = req.params;

    const user = await User.findById(userId).select('username wins losses draws score');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: error.message });
  }
};

exports.updateUser = async (req, res) => {
  try {
    const { userId } = req.params;
    const { username } = req.body;

    if (!username) {
      return res.status(400).json({ error: 'Username is required' });
    }

    const user = await User.findByIdAndUpdate(
      userId,
      { username },
      { new: true, runValidators: true }
    ).select('username');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ success: true, username: user.username });
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Username already exists' });
    }
    if (error.name === 'ValidationError') {
      return res.status(400).json({ error: error.message });
    }
    res.status(500).json({ error: error.message });
  }
};

exports.getMatchHistory = async (req, res) => {
  try {
    const { userId } = req.params;
    const limit = parseInt(req.query.limit) || 10;
    const page = parseInt(req.query.page) || 1;
    const skip = (page - 1) * limit;

    const userExists = await User.exists({ _id: userId });
    if (!userExists) {
      return res.status(404).json({ error: 'User not found' });
    }

    const total = await Match.countDocuments({
      $or: [{ player1: userId }, { player2: userId }]
    });

    const matches = await Match.find({
      $or: [{ player1: userId }, { player2: userId }]
    })
      .populate('player1', 'username')
      .populate('player2', 'username')
      .sort({ playedAt: -1 })
      .skip(skip)
      .limit(limit);

    const history = matches.map(match => {
      const opponent = match.player1._id.toString() === userId
        ? match.player2
        : match.player1;

      let winnerResult;
      if (!match.winner) {
        winnerResult = 'draw';
      } else if (match.winner.toString() === userId) {
        winnerResult = 'you';
      } else {
        winnerResult = opponent.username;
      }

      return {
        playedAt: match.playedAt,
        opponent: opponent.username,
        winner: winnerResult,
        moves: {
          p1Move: match.moves.p1Move,
          p2Move: match.moves.p2Move
        }
      };
    });

    res.json({ total, page, matches: history });
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).json({ error: 'User not found' });
    }
    res.status(500).json({ error: error.message });
  }
};

exports.getMatch = async (req, res) => {
  try {
    const { matchId } = req.params;

    const match = await Match.findById(matchId)
      .populate('player1', 'username')
      .populate('player2', 'username')
      .populate('winner', 'username');

    if (!match) {
      return res.status(404).json({ error: 'Match not found' });
    }

    res.json({
      _id: match._id,
      player1: match.player1.username,
      player2: match.player2.username,
      winner: match.winner ? match.winner.username : null,
      moves: match.moves,
      playedAt: match.playedAt
    });
  } catch (error) {
    if (error.kind === 'ObjectId') {
      return res.status(404).json({ error: 'Match not found' });
    }
    res.status(500).json({ error: error.message });
  }
};

exports.getLeaderboard = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;

    const users = await User.find()
      .sort({ score: -1 })
      .limit(limit)
      .select('_id username score wins');

    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getStats = async (req, res) => {
  try {
    const totalUsers = await User.countDocuments();
    const totalMatchesPlayed = await Match.countDocuments();

    res.json({ totalUsers, totalMatchesPlayed });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
