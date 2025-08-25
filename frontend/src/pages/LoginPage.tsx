/**
 * Login page component.
 */

import React, { useState } from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { useUser } from '../hooks/useUser';
import { ROUTES } from '../utils/constants';

export const LoginPage: React.FC = () => {
  const { isAuthenticated, isLoading } = useUser();
  const [showRegister, setShowRegister] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  if (isLoading) {
    return null; // Let the UserContext handle loading state
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #0ABAB5 0%, #00009C 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        {/* Header */}
        <Box textAlign="center" sx={{ mb: 4 }}>
          <Typography 
            variant="h3" 
            component="h1" 
            sx={{ 
              color: 'white',
              fontWeight: 'bold',
              mb: 1,
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
            }}
          >
            Biweekly Budget
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'rgba(255,255,255,0.9)',
              textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
            }}
          >
            Take control of your biweekly budget
          </Typography>
        </Box>

        {/* Auth Forms */}
        {showRegister ? (
          <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
        )}

        {/* Features Section */}
        <Paper 
          elevation={1} 
          sx={{ 
            mt: 4, 
            p: 3, 
            bgcolor: 'rgba(255,255,255,0.95)',
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" gutterBottom align="center" color="primary">
            Why Choose Biweekly Budget?
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              ✓ <strong>Biweekly Focus:</strong> Budget aligned with your actual paycheck cycle
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              ✓ <strong>Easy Tracking:</strong> Simple expense tracking with budget monitoring
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              ✓ <strong>Smart Analytics:</strong> Insights into your spending patterns
            </Typography>
            <Typography variant="body2">
              ✓ <strong>Always Free:</strong> No hidden fees or subscription costs
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};