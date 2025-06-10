import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box, IconButton } from '@mui/material';
import { School as SchoolIcon, Search as SearchIcon } from '@mui/icons-material';

interface HeaderProps {
  title?: string;
}

/**
 * Application header component with modern design
 */
const Header: React.FC<HeaderProps> = ({ title = 'Scholarship Database' }) => {
  return (
    <AppBar position="static" elevation={0}>
      <Container maxWidth="xl">
        <Toolbar sx={{ py: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                borderRadius: 2,
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
              }}
            >
              <SchoolIcon sx={{ fontSize: 28, color: 'white' }} />
            </Box>
            <Box>
              <Typography 
                variant="h5" 
                component="div" 
                sx={{ 
                  fontWeight: 700,
                  color: 'white',
                  letterSpacing: '-0.025em',
                }}
              >
                {title}
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontWeight: 400,
                }}
              >
                Find your perfect funding opportunity
              </Typography>
            </Box>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;