import { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../context/SocketContext';
import { useAuth } from '../context/AuthContext';

const GameState = {
  IDLE: 'IDLE',
  SEARCHING: 'SEARCHING',
  PLAYING: 'PLAYING',
  WAITING_OPPONENT: 'WAITING_OPPONENT',
  RESULT: 'RESULT',
  ABORTED: 'ABORTED'
};

const Arena = () => {
  const { socket } = useSocket();
  const { userId } = useAuth();
  const [state, setState] = useState(GameState.IDLE);
  const [opponentName, setOpponentName] = useState('');
  const [myMove, setMyMove] = useState(null);
  const [opponentMove, setOpponentMove] = useState(null);
  const [opponentHasMoved, setOpponentHasMoved] = useState(false);
  const [resultMessage, setResultMessage] = useState('');
  const [winnerId, setWinnerId] = useState(null);
  const [roomId, setRoomId] = useState(null);

  useEffect(() => {
    if (!socket || !userId) return;

    socket.emit('reconnect_attempt', { userId });

    const handleGameStarted = ({ roomId: rId, opponentName: name }) => {
      setRoomId(rId);
      setOpponentName(name);
      setMyMove(null);
      setOpponentMove(null);
      setOpponentHasMoved(false);
      setState(GameState.PLAYING);
    };

    const handleQueueLeft = () => {
      setState(GameState.IDLE);
    };

    const handleOpponentMoved = ({ hasMoved }) => {
      if (hasMoved) {
        setOpponentHasMoved(true);
      }
    };

    const handleRoundResult = ({ winnerId: wId, myMove: resultMyMove, opponentMove: oppMove, message }) => {
      setWinnerId(wId);
      setMyMove(resultMyMove);
      setOpponentMove(oppMove);
      setOpponentHasMoved(true);
      setResultMessage(message);
      setState(GameState.RESULT);
    };

    const handleStateRecovered = ({ roomId: rId, myMove: mMove, opponentHasMoved: oppHasMoved, opponentName: name }) => {
      setRoomId(rId);
      setOpponentName(name);
      setMyMove(mMove);
      setOpponentHasMoved(oppHasMoved);
      if (mMove) {
        setState(oppHasMoved ? GameState.RESULT : GameState.WAITING_OPPONENT);
      } else {
        setState(GameState.PLAYING);
      }
    };

    const handleOpponentDisconnected = () => {
      setState(GameState.ABORTED);
    };

    const handleStateNotFound = () => {
      // This is expected on fresh sessions and should not cancel active queueing.
    };

    const handleError = ({ code }) => {
      if (['SERVER_ERROR', 'INVALID_PAYLOAD', 'ALREADY_IN_QUEUE', 'NOT_IN_QUEUE'].includes(code)) {
        setState(GameState.IDLE);
      }
    };

    socket.on('game_started', handleGameStarted);
    socket.on('queue_left', handleQueueLeft);
    socket.on('opponent_moved', handleOpponentMoved);
    socket.on('round_result', handleRoundResult);
    socket.on('state_recovered', handleStateRecovered);
    socket.on('state_not_found', handleStateNotFound);
    socket.on('opponent_disconnected', handleOpponentDisconnected);
    socket.on('error', handleError);

    return () => {
      socket.off('game_started', handleGameStarted);
      socket.off('queue_left', handleQueueLeft);
      socket.off('opponent_moved', handleOpponentMoved);
      socket.off('round_result', handleRoundResult);
      socket.off('state_recovered', handleStateRecovered);
      socket.off('state_not_found', handleStateNotFound);
      socket.off('opponent_disconnected', handleOpponentDisconnected);
      socket.off('error', handleError);
    };
  }, [socket, userId]);

  const handleFindGame = () => {
    setState(GameState.SEARCHING);
    socket.emit('join_queue', { userId });
  };

  const handleCancel = () => {
    socket.emit('leave_queue', { userId });
    setState(GameState.IDLE);
  };

  const handleMakeMove = (move) => {
    socket.emit('make_move', { roomId, userId, move });
    setMyMove(move);
    setState(GameState.WAITING_OPPONENT);
  };

  const handleNextMatch = () => {
    setMyMove(null);
    setOpponentMove(null);
    setOpponentHasMoved(false);
    setResultMessage('');
    setWinnerId(null);
    setRoomId(null);
    setState(GameState.IDLE);
  };

  const handleReturnToLobby = () => {
    setState(GameState.IDLE);
  };

  const renderContent = () => {
    switch (state) {
      case GameState.IDLE:
        return (
          <div style={styles.centered}>
            <h2 style={styles.heading}>Ready to Play?</h2>
            <button onClick={handleFindGame} style={styles.playBtn}>Find Game</button>
          </div>
        );
      case GameState.SEARCHING:
        return (
          <div style={styles.centered}>
            <div style={styles.spinner}></div>
            <p>Searching for opponent...</p>
            <button onClick={handleCancel} style={styles.cancelBtn}>Cancel</button>
          </div>
        );
      case GameState.PLAYING:
      case GameState.WAITING_OPPONENT:
        const isMyMoveLocked = Boolean(myMove);
        return (
          <div style={styles.arena}>
            <h2 style={styles.heading}>VS {opponentName}</h2>
            <div style={styles.players}>
              <div style={styles.playerCard}>
                <p>You</p>
                {myMove && <span style={styles.moveIcon}>{myMove === 'rock' ? '🪨' : myMove === 'paper' ? '📄' : '✂️'}</span>}
              </div>
              <div style={styles.playerCard}>
                <p>{opponentName}</p>
                {isMyMoveLocked && !opponentHasMoved ? <span>Waiting...</span> : opponentMove && <span style={styles.moveIcon}>{opponentMove === 'rock' ? '🪨' : opponentMove === 'paper' ? '📄' : '✂️'}</span>}
              </div>
            </div>
            <div style={styles.moves}>
              {['rock', 'paper', 'scissors'].map((move) => (
                <button
                  key={move}
                  onClick={() => handleMakeMove(move)}
                  disabled={isMyMoveLocked}
                  style={isMyMoveLocked ? styles.moveBtnDisabled : styles.moveBtn}
                >
                  {move === 'rock' ? '🪨' : move === 'paper' ? '📄' : '✂️'}
                </button>
              ))}
            </div>
            {isMyMoveLocked && <p style={styles.waiting}>Waiting for opponent...</p>}
          </div>
        );
      case GameState.RESULT:
        const isWinner = winnerId === userId;
        return (
          <div style={styles.centered}>
            <h2 style={styles.heading}>{resultMessage}</h2>
            <div style={styles.resultMoves}>
              <div style={styles.moveCard}>
                <p>Your move</p>
                <span style={styles.moveIcon}>{myMove === 'rock' ? '🪨' : myMove === 'paper' ? '📄' : '✂️'}</span>
              </div>
              <div style={styles.moveCard}>
                <p>{opponentName}'s move</p>
                <span style={styles.moveIcon}>{opponentMove === 'rock' ? '🪨' : opponentMove === 'paper' ? '📄' : '✂️'}</span>
              </div>
            </div>
            <button onClick={handleNextMatch} style={styles.playBtn}>Next Match</button>
          </div>
        );
      case GameState.ABORTED:
        return (
          <div style={styles.centered}>
            <h2 style={styles.heading}>Opponent disconnected.</h2>
            <button onClick={handleReturnToLobby} style={styles.playBtn}>Return to Lobby</button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div style={styles.container}>
      {renderContent()}
    </div>
  );
};

const styles = {
  container: { maxWidth: '600px', margin: '0 auto' },
  centered: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '1rem' },
  arena: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' },
  heading: { color: '#fff', fontSize: '1.8rem', margin: 0 },
  playBtn: { padding: '14px 40px', borderRadius: '8px', border: 'none', background: '#e94560', color: '#fff', fontSize: '1.1rem', cursor: 'pointer', fontWeight: 'bold' },
  cancelBtn: { padding: '10px 30px', borderRadius: '6px', border: '1px solid #a0a0a0', background: 'transparent', color: '#a0a0a0', cursor: 'pointer' },
  spinner: { width: '40px', height: '40px', border: '4px solid #16213e', borderTop: '4px solid #e94560', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' },
  players: { display: 'flex', gap: '3rem' },
  playerCard: { background: '#16213e', padding: '1.5rem', borderRadius: '10px', textAlign: 'center', minWidth: '120px', color: '#fff' },
  moves: { display: 'flex', gap: '1rem' },
  moveBtn: { padding: '1rem 1.5rem', borderRadius: '8px', border: 'none', background: '#0f3460', color: '#fff', fontSize: '2rem', cursor: 'pointer' },
  moveBtnDisabled: { padding: '1rem 1.5rem', borderRadius: '8px', border: 'none', background: '#0f3460', color: '#666', fontSize: '2rem', cursor: 'not-allowed' },
  moveIcon: { fontSize: '2.5rem' },
  waiting: { color: '#a0a0a0' },
  resultMoves: { display: 'flex', gap: '2rem' },
  moveCard: { background: '#16213e', padding: '1.5rem', borderRadius: '10px', textAlign: 'center', color: '#fff' }
};

export default Arena;
