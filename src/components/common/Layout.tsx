import React from 'react';
import { Container, Box } from '@mui/material';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

/**
 * Main layout component with modern spacing and structure
 */
const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        backgroundColor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Header title={title} />
      <Box sx={{ flex: 1 }}>
        <Container 
          maxWidth="xl" 
          sx={{ 
            py: { xs: 3, sm: 4, md: 6 },
            px: { xs: 2, sm: 3 },
          }}
        >
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;