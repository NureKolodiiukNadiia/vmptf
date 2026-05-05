import { useState, useEffect } from 'react';

const Leaderboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:3000/api/leaderboard')
      .then(res => res.json())
      .then(data => {
        setUsers(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

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
      <h2 style={styles.heading}>Leaderboard</h2>
      <table style={styles.table}>
        <thead>
          <tr style={styles.headerRow}>
            <th style={styles.th}>Rank</th>
            <th style={styles.th}>Username</th>
            <th style={styles.th}>Score</th>
            <th style={styles.th}>Win Rate</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, index) => {
            const totalMatches = user.wins;
            const winRate = totalMatches > 0 ? '100%' : '0%';
            return (
              <tr key={user._id} style={styles.row}>
                <td style={styles.td}>{index + 1}</td>
                <td style={styles.td}>{user.username}</td>
                <td style={styles.td}>{user.score}</td>
                <td style={styles.td}>{winRate}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

const styles = {
  container: { maxWidth: '800px', margin: '0 auto' },
  heading: { color: '#fff', textAlign: 'center', marginBottom: '2rem' },
  table: { width: '100%', borderCollapse: 'collapse', background: '#16213e', borderRadius: '10px', overflow: 'hidden' },
  headerRow: { background: '#0f3460' },
  th: { padding: '1rem', textAlign: 'left', color: '#a0a0a0', fontWeight: 'normal' },
  row: { borderBottom: '1px solid #0f3460' },
  td: { padding: '1rem', color: '#fff' },
  skeleton: { height: '50px', background: '#16213e', marginBottom: '10px', borderRadius: '6px', animation: 'pulse 1.5s infinite' }
};

export default Leaderboard;