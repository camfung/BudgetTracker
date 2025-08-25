/**
 * Main App component with routing and providers.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import { UserProvider } from './contexts/UserContext';
import { BudgetProvider } from './contexts/BudgetContext';
import { TransactionProvider } from './contexts/TransactionContext';
import { PrivateRoute } from './components/auth/PrivateRoute';
import { InstallBanner } from './components/pwa/InstallBanner';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { BudgetPage } from './pages/BudgetPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { HistoryPage } from './pages/HistoryPage';
import { theme } from './theme/theme';
import { ROUTES } from './utils/constants';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <UserProvider>
        <AuthProvider>
          <BudgetProvider>
            <TransactionProvider>
              <Router>
                <Routes>
                  {/* Public Routes */}
                  <Route path={ROUTES.LOGIN} element={<LoginPage />} />
                  
                  {/* Private Routes */}
                  <Route 
                    path={ROUTES.DASHBOARD} 
                    element={
                      <PrivateRoute>
                        <DashboardPage />
                      </PrivateRoute>
                    } 
                  />
                  <Route 
                    path={ROUTES.BUDGET} 
                    element={
                      <PrivateRoute>
                        <BudgetPage />
                      </PrivateRoute>
                    } 
                  />
                  <Route 
                    path={ROUTES.TRANSACTIONS} 
                    element={
                      <PrivateRoute>
                        <TransactionsPage />
                      </PrivateRoute>
                    } 
                  />
                  <Route 
                    path={ROUTES.HISTORY} 
                    element={
                      <PrivateRoute>
                        <HistoryPage />
                      </PrivateRoute>
                    } 
                  />
                  
                  {/* Default redirect */}
                  <Route path="/" element={<LoginPage />} />
                </Routes>
              </Router>
              <InstallBanner />
            </TransactionProvider>
          </BudgetProvider>
        </AuthProvider>
      </UserProvider>
    </ThemeProvider>
  );
};

export default App;