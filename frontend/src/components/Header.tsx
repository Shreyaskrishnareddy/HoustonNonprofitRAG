import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="static" sx={{ 
      background: 'rgba(255, 255, 255, 0.15)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.18)',
      boxShadow: '0 4px 32px 0 rgba(31, 38, 135, 0.2)',
    }}>
      <Toolbar>
        <Typography variant="h5" component="div" sx={{ 
          flexGrow: 1,
          fontWeight: 700,
          background: 'linear-gradient(135deg, #007AFF 0%, #34C759 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          Houston Impact Explorer
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            color="inherit"
            component={Link}
            to="/"
            sx={{
              color: '#1D1D1F',
              backgroundColor: isActive('/') ? 'rgba(0, 122, 255, 0.15)' : 'transparent',
              borderRadius: '12px',
              padding: '8px 16px',
              fontWeight: 600,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: 'rgba(0, 122, 255, 0.1)',
                transform: 'translateY(-1px)',
              }
            }}
          >
            🏠 Overview
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/nonprofits"
            sx={{
              color: '#1D1D1F',
              backgroundColor: isActive('/nonprofits') ? 'rgba(0, 122, 255, 0.15)' : 'transparent',
              borderRadius: '12px',
              padding: '8px 16px',
              fontWeight: 600,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: 'rgba(0, 122, 255, 0.1)',
                transform: 'translateY(-1px)',
              }
            }}
          >
            🏢 Organizations
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/chat"
            sx={{
              color: '#1D1D1F',
              backgroundColor: isActive('/chat') ? 'rgba(52, 199, 89, 0.15)' : 'transparent',
              borderRadius: '12px',
              padding: '8px 16px',
              fontWeight: 600,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: 'rgba(52, 199, 89, 0.1)',
                transform: 'translateY(-1px)',
              }
            }}
          >
            🤖 AI Explorer
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;