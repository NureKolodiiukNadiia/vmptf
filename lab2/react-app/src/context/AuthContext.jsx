import { createContext, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [userId, setUserId] = useState(() => localStorage.getItem('userId'));
  const [username, setUsername] = useState(() => localStorage.getItem('username'));
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('userId'));
  const navigate = useNavigate();

  const login = async (inputUsername) => {
    const response = await fetch('http://localhost:3000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: inputUsername })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    localStorage.setItem('userId', data.userId);
    localStorage.setItem('username', data.username);
    setUserId(data.userId);
    setUsername(data.username);
    setIsAuthenticated(true);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    setUserId(null);
    setUsername(null);
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ userId, username, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);