/**
 * Material-UI theme configuration with custom color palette.
 */

import { createTheme } from '@mui/material/styles';

// Custom color palette as specified in the PRP
const colors = {
  thistle: '#D8BFD8',      // Light purple
  azureWeb: '#F0F8FF',     // Light blue
  gold: '#FFD700',         // Gold
  tiffanyBlue: '#0ABAB5',  // Teal
  dukeBlue: '#00009C',     // Dark blue
};

declare module '@mui/material/styles' {
  interface Palette {
    accent: {
      thistle: string;
      azureWeb: string;
      gold: string;
      tiffanyBlue: string;
      dukeBlue: string;
    };
  }

  interface PaletteOptions {
    accent?: {
      thistle?: string;
      azureWeb?: string;
      gold?: string;
      tiffanyBlue?: string;
      dukeBlue?: string;
    };
  }
}

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: colors.dukeBlue,
      light: '#3333B3',
      dark: '#000074',
      contrastText: '#ffffff',
    },
    secondary: {
      main: colors.tiffanyBlue,
      light: '#4BCBC6',
      dark: '#078A85',
      contrastText: '#ffffff',
    },
    accent: {
      thistle: colors.thistle,
      azureWeb: colors.azureWeb,
      gold: colors.gold,
      tiffanyBlue: colors.tiffanyBlue,
      dukeBlue: colors.dukeBlue,
    },
    background: {
      default: colors.azureWeb,
      paper: '#ffffff',
    },
    text: {
      primary: '#1a1a1a',
      secondary: '#666666',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: colors.gold,
    },
    error: {
      main: '#f44336',
    },
    info: {
      main: colors.tiffanyBlue,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: colors.dukeBlue,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: colors.dukeBlue,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      color: colors.dukeBlue,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 24px',
          fontWeight: 500,
        },
        contained: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.dukeBlue,
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
        },
        bar: {
          borderRadius: 4,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
  },
});

export default theme;