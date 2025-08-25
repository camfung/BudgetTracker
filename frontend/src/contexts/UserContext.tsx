/**
 * User context for managing authentication state.
 */

import { createContext, useState, useEffect, ReactNode } from 'react';
import { User, TokenResponse } from '../types/user';
import { getCurrentUser } from '../services/auth.service';

export interface UserContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (tokenResponse: TokenResponse) => void;
  logout: () => void;
  updateUser: (updatedUser: User) => void;
}

export const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Login function to store the user and tokens
  const login = (tokenResponse: TokenResponse) => {
    setUser(tokenResponse.user);
    localStorage.setItem('user', JSON.stringify(tokenResponse.user));
    localStorage.setItem('access_token', tokenResponse.access_token);
    localStorage.setItem('refresh_token', tokenResponse.refresh_token);
  };

  // Logout function to clear the user and tokens
  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  // Update user information
  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  useEffect(() => {
    // On mount, validate the token and fetch the user if valid
    const validateSession = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const fetchedUser = await getCurrentUser();
        setUser(fetchedUser);
        localStorage.setItem('user', JSON.stringify(fetchedUser));
      } catch (error) {
        console.error('Failed to validate session:', error);
        // Clear invalid tokens
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    validateSession();
  }, []);

  const value: UserContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    updateUser,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};