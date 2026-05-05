import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../context/SocketContext';
import { useEffect, useState } from 'react';

const Layout = () => {
  const { username, logout } = useAuth();
  const { socket, isConnected } = useSocket();
  const [reconnecting, setReconnecting] = useState(false);

  useEffect(() => {
    if (!isConnected && socket) {
      const onConnect = () => setReconnecting(false);
      const onDisconnect = () => setReconnecting(true);
      socket.on('connect', onConnect);
      socket.on('disconnect', onDisconnect);
      return () => {
        socket.off('connect', onConnect);
        socket.off('disconnect', onDisconnect);
      };
    }
  }, [socket, isConnected]);

  return (
    <div style={styles.app}>
      {reconnecting && !isConnected && (
        <div style={styles.overlay}>
          <p>Connection lost. Reconnecting...</p>
        </div>
      )}
      <nav style={styles.nav}>
        <div style={styles.navLeft}>
          <span style={styles.logo}>RPS Game</span>
          <NavLink to="/" style={({ isActive }) => isActive ? styles.active : styles.link}>Play</NavLink>
          <NavLink to="/leaderboard" style={({ isActive }) => isActive ? styles.active : styles.link}>Leaderboard</NavLink>
          <NavLink to="/history" style={({ isActive }) => isActive ? styles.active : styles.link}>History</NavLink>
        </div>
        <div style={styles.navRight}>
          <span style={styles.username}>{username}</span>
          <button onClick={logout} style={styles.logoutBtn}>Logout</button>
        </div>
      </nav>
      <main style={styles.main}>
        <Outlet />
      </main>
    </div>
  );
};

const styles = {
  app: { minHeight: '100vh', background: '#1a1a2e' },
  nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', background: '#16213e', borderBottom: '1px solid #0f3460' },
  navLeft: { display: 'flex', gap: '1.5rem', alignItems: 'center' },
  navRight: { display: 'flex', gap: '1rem', alignItems: 'center' },
  logo: { color: '#e94560', fontWeight: 'bold', fontSize: '1.2rem' },
  link: { color: '#a0a0a0', textDecoration: 'none', fontSize: '0.95rem' },
  active: { color: '#e94560', textDecoration: 'none', fontSize: '0.95rem' },
  username: { color: '#fff' },
  logoutBtn: { background: 'transparent', border: '1px solid #e94560', color: '#e94560', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' },
  main: { padding: '2rem' },
  overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, color: '#fff', fontSize: '1.2rem' }
};

export default Layout;