import React from 'react';
import { Container, Box } from '@mui/material';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

/**
 * Main layout component that wraps the entire application
 */
const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Header title={title} />
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;
