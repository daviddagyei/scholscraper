import React from 'react';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import { School as SchoolIcon } from '@mui/icons-material';

interface HeaderProps {
  title?: string;
}

/**
 * Application header component
 */
const Header: React.FC<HeaderProps> = ({ title = 'Scholarship Database' }) => {
  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <SchoolIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
