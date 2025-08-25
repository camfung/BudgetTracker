/**
 * Main layout wrapper component.
 */

import React from 'react';
import { Box, Container, useTheme, useMediaQuery } from '@mui/material';
import { Navbar } from './Navbar';

interface LayoutProps {
  children: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
}

export const Layout: React.FC<LayoutProps> = ({ children, maxWidth = 'lg' }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 3,
          px: { xs: 2, sm: 3 },
          bgcolor: 'background.default',
        }}
      >
        <Container maxWidth={maxWidth} disableGutters={isMobile}>
          {children}
        </Container>
      </Box>
      
      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 3,
          mt: 'auto',
          bgcolor: 'grey.100',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Container maxWidth={maxWidth}>
          <Box textAlign="center">
            <Box
              component="span"
              sx={{ 
                fontSize: '0.875rem', 
                color: 'text.secondary',
              }}
            >
              © {new Date().getFullYear()} Biweekly Budget App. 
              Made with ❤️ for better financial planning.
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};