const socketIO = require('socket.io');
const GameState = require('./models/GameState');
const Match = require('./models/Match');
const User = require('./models/User');

let io;

const socketMap = new Map();

const findSocketByUserId = (userId) => Array.from(io.sockets.sockets.values())
  .find((connectedSocket) => socketMap.get(connectedSocket.id)?.userId === userId);

const initializeSocket = (server) => {
  io = socketIO(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST']
    }
  });

  io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);

    socket.on('join_queue', async (data) => {
      await handleJoinQueue(socket, data);
    });

    socket.on('leave_queue', async (data) => {
      await handleLeaveQueue(socket, data);
    });

    socket.on('make_move', async (data) => {
      await handleMakeMove(socket, data);
    });

    socket.on('reconnect_attempt', async (data) => {
      await handleReconnectAttempt(socket, data);
    });

    socket.on('disconnect', async () => {
      await handleDisconnect(socket);
    });
  });

  return io;
};

const handleJoinQueue = async (socket, { userId }) => {
  try {
    if (!userId) {
      return socket.emit('error', { message: 'User ID is required', code: 'INVALID_PAYLOAD' });
    }

    const ownWaitingGame = await GameState.findOne({
      status: 'waiting',
      players: userId
    });

    if (ownWaitingGame) {
      return socket.emit('error', { message: 'Already in queue', code: 'ALREADY_IN_QUEUE' });
    }

    const existingGame = await GameState.findOne({
      $and: [
        { status: 'waiting' },
        { players: { $size: 1 } },
        { players: { $ne: userId } }
      ]
    });

    if (existingGame) {
      existingGame.players.push(userId);
      existingGame.status = 'playing';
      await existingGame.save();

      const roomId = existingGame.roomId;
      socket.join(roomId);
      socketMap.set(socket.id, { userId, roomId });

      const [playerOne, playerTwo] = await Promise.all([
        User.findById(existingGame.players[0]).select('username'),
        User.findById(existingGame.players[1]).select('username')
      ]);

      const waitingPlayerSocket = findSocketByUserId(existingGame.players[0].toString());

      if (waitingPlayerSocket) {
        waitingPlayerSocket.join(roomId);
        socketMap.set(waitingPlayerSocket.id, {
          userId: existingGame.players[0].toString(),
          roomId
        });
      }

      socket.to(roomId).emit('game_started', {
        roomId,
        opponentName: playerTwo ? playerTwo.username : 'Opponent'
      });

      socket.emit('game_started', {
        roomId,
        opponentName: playerOne ? playerOne.username : 'Opponent'
      });
    } else {
      const roomId = `room_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const newGame = await GameState.create({
        roomId,
        players: [userId],
        status: 'waiting',
        moves: new Map()
      });

      socket.join(roomId);
      socketMap.set(socket.id, { userId, roomId });
    }
  } catch (error) {
    socket.emit('error', { message: error.message, code: 'SERVER_ERROR' });
  }
};

const handleLeaveQueue = async (socket, { userId }) => {
  try {
    const mapping = socketMap.get(socket.id);
    if (!mapping) {
      return socket.emit('error', { message: 'Not in any queue', code: 'NOT_IN_QUEUE' });
    }

    const gameState = await GameState.findOne({
      roomId: mapping.roomId,
      status: 'waiting',
      players: userId
    });

    if (gameState) {
      await GameState.deleteOne({ _id: gameState._id });
      socket.leave(mapping.roomId);
      socketMap.delete(socket.id);
      socket.emit('queue_left', { success: true });
    } else {
      socket.emit('error', { message: 'Not in waiting queue', code: 'NOT_IN_QUEUE' });
    }
  } catch (error) {
    socket.emit('error', { message: error.message, code: 'SERVER_ERROR' });
  }
};

const handleMakeMove = async (socket, { roomId, userId, move }) => {
  try {
    if (!roomId || !userId || !move) {
      return socket.emit('error', { message: 'Invalid payload', code: 'INVALID_PAYLOAD' });
    }

    const validMoves = ['rock', 'paper', 'scissors'];
    if (!validMoves.includes(move)) {
      return socket.emit('error', { message: 'Invalid move', code: 'INVALID_MOVE' });
    }

    const gameState = await GameState.findOne({ roomId, status: 'playing' });
    if (!gameState) {
      return socket.emit('error', { message: 'Game not found', code: 'GAME_NOT_FOUND' });
    }

    const userIndex = gameState.players.findIndex(p => p.toString() === userId);
    if (userIndex === -1) {
      return socket.emit('error', { message: 'Not a player in this game', code: 'NOT_PLAYER' });
    }

    const movesMap = gameState.moves;
    const playerKey = userId.toString();

    if (movesMap.has(playerKey)) {
      return socket.emit('error', { message: 'Already made a move', code: 'MOVE_ALREADY_MADE' });
    }

    movesMap.set(playerKey, move);
    gameState.moves = movesMap;
    await gameState.save();

    const otherPlayerId = gameState.players.find(p => p.toString() !== userId);
    const otherSocket = findSocketByUserId(otherPlayerId?.toString());

    if (otherSocket) {
      otherSocket.emit('opponent_moved', { hasMoved: true });
    }

    socket.emit('opponent_moved', { hasMoved: false });

    if (movesMap.size === 2) {
      await resolveGame(gameState);
    }
  } catch (error) {
    socket.emit('error', { message: error.message, code: 'SERVER_ERROR' });
  }
};

const resolveGame = async (gameState) => {
  const { roomId, players, moves: movesMap } = gameState;

  const player1Id = players[0].toString();
  const player2Id = players[1].toString();

  const p1Move = movesMap.get(player1Id);
  const p2Move = movesMap.get(player2Id);

  let winnerId = null;
  let message = '';

  const [user1, user2] = await Promise.all([
    User.findById(player1Id),
    User.findById(player2Id)
  ]);

  const isDraw = p1Move === p2Move;
  const playerOneWins = !isDraw && (
    (p1Move === 'rock' && p2Move === 'scissors') ||
    (p1Move === 'paper' && p2Move === 'rock') ||
    (p1Move === 'scissors' && p2Move === 'paper')
  );

  if (isDraw) {
    message = "It's a draw!";
  } else if (playerOneWins) {
    winnerId = player1Id;
    message = `${user1.username} wins!`;
  } else {
    winnerId = player2Id;
    message = `${user2.username} wins!`;
  }

  if (isDraw) {
    user1.draws += 1;
    user2.draws += 1;
  } else if (playerOneWins) {
    user1.wins += 1;
    user2.losses += 1;
  } else {
    user2.wins += 1;
    user1.losses += 1;
  }

  await Promise.all([user1.save(), user2.save()]);

  await Match.create({
    player1: player1Id,
    player2: player2Id,
    winner: winnerId,
    moves: { p1Move, p2Move },
    playedAt: new Date()
  });

  const playerOneSocket = findSocketByUserId(player1Id);
  const playerTwoSocket = findSocketByUserId(player2Id);
  const basePayload = { winnerId, message };

  if (playerOneSocket) {
    playerOneSocket.emit('round_result', {
      ...basePayload,
      myMove: p1Move,
      opponentMove: p2Move
    });
  }

  if (playerTwoSocket) {
    playerTwoSocket.emit('round_result', {
      ...basePayload,
      myMove: p2Move,
      opponentMove: p1Move
    });
  }

  await GameState.deleteOne({ _id: gameState._id });
};

const handleReconnectAttempt = async (socket, { userId }) => {
  try {
    const gameState = await GameState.findOne({
      status: 'playing',
      players: userId
    });

    if (!gameState) {
      return socket.emit('state_not_found', { message: 'No active game found' });
    }

    socket.join(gameState.roomId);
    socketMap.set(socket.id, { userId, roomId: gameState.roomId });

    const movesMap = gameState.moves;
    const playerKey = userId.toString();
    const myMove = movesMap.get(playerKey) || null;

    const otherPlayerId = gameState.players.find(p => p.toString() !== userId);
    const opponent = await User.findById(otherPlayerId).select('username');
    const opponentHasMoved = movesMap.has(otherPlayerId.toString());

    socket.emit('state_recovered', {
      roomId: gameState.roomId,
      myMove,
      opponentHasMoved,
      opponentName: opponent ? opponent.username : 'Opponent'
    });
  } catch (error) {
    socket.emit('error', { message: error.message, code: 'SERVER_ERROR' });
  }
};

const handleDisconnect = async (socket) => {
  try {
    const mapping = socketMap.get(socket.id);
    if (!mapping) {
      return;
    }

    const { userId, roomId } = mapping;

    const gameState = await GameState.findOne({
      roomId,
      status: 'playing',
      players: userId
    });

    if (gameState) {
      const otherPlayerId = gameState.players.find(p => p.toString() !== userId);
      await GameState.deleteOne({ _id: gameState._id });

      io.to(roomId).emit('opponent_disconnected', { message: 'Opponent left the match.' });
    }

    socketMap.delete(socket.id);
  } catch (error) {
    console.error('Disconnect handler error:', error);
  }
};

module.exports = initializeSocket;
