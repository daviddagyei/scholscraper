import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';


interface HeaderProps {
  title?: string;
}

/**
 * Application header component with modern design
 */
const Header: React.FC<HeaderProps> = ({ title = 'Scholarship Hub' }) => {
  return (
    <AppBar position="static" elevation={0}>
      <Container maxWidth="xl" sx={{ pl: { xs: 1, sm: 2 } }}>
        <Toolbar sx={{ py: 1, pl: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: 48,
                borderRadius: 2,
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                px: 1,
              }}
            >
              <img 
                src="/palouse-pathways-logo.png" 
                alt="Palouse Pathways Logo" 
                style={{ 
                  height: 40, 
                  width: 'auto'
                }} 
              />
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