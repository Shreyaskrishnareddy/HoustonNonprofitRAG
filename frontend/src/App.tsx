import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import NonprofitList from './pages/NonprofitList';
import NonprofitDetail from './pages/NonprofitDetail';
import Chat from './pages/Chat';

// Apple-inspired glassmorphism theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#007AFF', // Apple blue
      light: '#5AC8FA',
      dark: '#0051D5',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#34C759', // Apple green
      light: '#30D158',
      dark: '#248A3D',
      contrastText: '#FFFFFF',
    },
    background: {
      default: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      paper: 'rgba(255, 255, 255, 0.25)',
    },
    text: {
      primary: '#1D1D1F',
      secondary: '#86868B',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.02em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.015em',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
      letterSpacing: '-0.005em',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.25)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.18)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 20px',
          backdropFilter: 'blur(20px)',
          transition: 'all 0.3s ease',
        },
        contained: {
          background: 'linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%)',
          boxShadow: '0 4px 15px 0 rgba(0, 122, 255, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #0051D5 0%, #007AFF 100%)',
            boxShadow: '0 6px 20px 0 rgba(0, 122, 255, 0.4)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.25)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.18)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px 0 rgba(31, 38, 135, 0.4)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            background: 'rgba(255, 255, 255, 0.25)',
            backdropFilter: 'blur(20px)',
            borderRadius: '12px',
            '& fieldset': {
              border: '1px solid rgba(255, 255, 255, 0.18)',
            },
            '&:hover fieldset': {
              border: '1px solid rgba(0, 122, 255, 0.5)',
            },
            '&.Mui-focused fieldset': {
              border: '2px solid #007AFF',
            },
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          backgroundAttachment: 'fixed',
        }}>
          <Header />
          <Box component="main" sx={{ 
            flexGrow: 1, 
            p: 3,
            position: 'relative',
          }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/nonprofits" element={<NonprofitList />} />
              <Route path="/nonprofit/:ein" element={<NonprofitDetail />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;