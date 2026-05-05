import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const History = () => {
  const { userId } = useAuth();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    fetch(`http://localhost:3000/api/matches/user/${userId}?page=${page}&limit=10`)
      .then(res => res.json())
      .then(data => {
        setMatches(data.matches || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [userId, page]);

  const getResultColor = (winner) => {
    if (winner === 'you') return '#4ade80';
    if (winner === 'draw') return '#a0a0a0';
    return '#ff6b6b';
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.skeleton}></div>
        <div style={styles.skeleton}></div>
        <div style={styles.skeleton}></div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Match History</h2>
      {matches.length === 0 ? (
        <p style={styles.empty}>No matches yet</p>
      ) : (
        <>
          <div style={styles.list}>
            {matches.map((match) => (
              <div key={match.playedAt} style={styles.matchCard}>
                <div style={styles.matchInfo}>
                  <span style={styles.opponent}>{match.opponent}</span>
                  <span style={styles.date}>
                    {new Date(match.playedAt).toLocaleDateString()}
                  </span>
                </div>
                <div style={styles.moves}>
                  <span>You: {match.moves?.p1Move || '-'}</span>
                  <span>Them: {match.moves?.p2Move || '-'}</span>
                </div>
                <div style={{ ...styles.result, color: getResultColor(match.winner) }}>
                  {match.winner === 'you' ? 'Win' : match.winner === 'draw' ? 'Draw' : 'Loss'}
                </div>
              </div>
            ))}
          </div>
          <div style={styles.pagination}>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              style={styles.pageBtn}
            >
              Previous
            </button>
            <span style={styles.pageInfo}>Page {page}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page * 10 >= total}
              style={styles.pageBtn}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

const styles = {
  container: { maxWidth: '800px', margin: '0 auto' },
  heading: { color: '#fff', textAlign: 'center', marginBottom: '2rem' },
  empty: { color: '#a0a0a0', textAlign: 'center' },
  list: { display: 'flex', flexDirection: 'column', gap: '10px' },
  matchCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#16213e', padding: '1rem', borderRadius: '8px' },
  matchInfo: { display: 'flex', flexDirection: 'column', gap: '4px' },
  opponent: { color: '#fff', fontWeight: 'bold' },
  date: { color: '#a0a0a0', fontSize: '0.85rem' },
  moves: { display: 'flex', gap: '1rem', color: '#a0a0a0' },
  result: { fontWeight: 'bold' },
  pagination: { display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2rem' },
  pageBtn: { padding: '8px 16px', borderRadius: '6px', border: 'none', background: '#e94560', color: '#fff', cursor: 'pointer' },
  pageInfo: { color: '#fff', display: 'flex', alignItems: 'center' },
  skeleton: { height: '60px', background: '#16213e', marginBottom: '10px', borderRadius: '8px', animation: 'pulse 1.5s infinite' }
};

export default History;