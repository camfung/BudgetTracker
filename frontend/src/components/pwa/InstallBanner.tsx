/**
 * PWA Install Banner component
 * Shows a banner prompting users to install the app
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  Slide,
  Alert,
} from '@mui/material';
import {
  GetApp as InstallIcon,
  Close as CloseIcon,
  Smartphone as PhoneIcon,
} from '@mui/icons-material';
import { showInstallPrompt, isInstallAvailable, isAppInstalled } from '../../utils/pwa';

export const InstallBanner: React.FC = () => {
  const [showBanner, setShowBanner] = useState(false);
  const [installing, setInstalling] = useState(false);

  useEffect(() => {
    // Check if we should show the install banner
    const checkInstallStatus = () => {
      // Don't show if already installed
      if (isAppInstalled()) {
        setShowBanner(false);
        return;
      }

      // Check if install prompt is available
      if (isInstallAvailable()) {
        // Show banner after a delay to not be intrusive
        const timer = setTimeout(() => {
          setShowBanner(true);
        }, 5000);

        return () => clearTimeout(timer);
      }
      
      return undefined;
    };

    const cleanup = checkInstallStatus();

    // Listen for install prompt availability
    const handleBeforeInstallPrompt = () => {
      if (!isAppInstalled()) {
        setShowBanner(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      if (cleanup) cleanup();
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstall = async () => {
    setInstalling(true);
    try {
      const accepted = await showInstallPrompt();
      if (accepted) {
        setShowBanner(false);
      }
    } catch (error) {
      console.error('Failed to install app:', error);
    } finally {
      setInstalling(false);
    }
  };

  const handleClose = () => {
    setShowBanner(false);
    // Don't show again for this session
    sessionStorage.setItem('installBannerDismissed', 'true');
  };

  // Don't show if dismissed in this session
  if (sessionStorage.getItem('installBannerDismissed')) {
    return null;
  }

  return (
    <Slide direction="up" in={showBanner} mountOnEnter unmountOnExit>
      <Box
        sx={{
          position: 'fixed',
          bottom: 16,
          left: 16,
          right: 16,
          zIndex: 1300,
          display: { xs: 'block', md: 'none' }, // Show only on mobile
        }}
      >
        <Alert
          severity="info"
          sx={{
            '& .MuiAlert-message': {
              display: 'flex',
              alignItems: 'center',
              width: '100%',
            },
          }}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Button
                color="primary"
                variant="contained"
                size="small"
                startIcon={<InstallIcon />}
                onClick={handleInstall}
                disabled={installing}
                sx={{ minWidth: 'auto' }}
              >
                {installing ? 'Installing...' : 'Install'}
              </Button>
              <IconButton
                size="small"
                onClick={handleClose}
                color="inherit"
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          }
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <PhoneIcon sx={{ mr: 1 }} />
            <Box>
              <Typography variant="body2" fontWeight="bold">
                Install GeminiPay
              </Typography>
              <Typography variant="caption">
                Add to your home screen for quick access
              </Typography>
            </Box>
          </Box>
        </Alert>
      </Box>
    </Slide>
  );
};