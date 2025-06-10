import React from 'react';
import {
  TextField,
  InputAdornment,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

interface SearchBarProps {
  searchTerm: string;
  onSearchChange: (searchTerm: string) => void;
  placeholder?: string;
}

/**
 * Search bar component with fuzzy search capability
 */
const SearchBar: React.FC<SearchBarProps> = ({
  searchTerm,
  onSearchChange,
  placeholder = 'Search scholarships by title, description, or provider...',
}) => {
  const handleClear = () => {
    onSearchChange('');
  };

  return (
    <Box sx={{ mb: 3 }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder={placeholder}
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
          endAdornment: searchTerm && (
            <InputAdornment position="end">
              <Tooltip title="Clear search">
                <IconButton
                  onClick={handleClear}
                  edge="end"
                  size="small"
                >
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'white',
            '&:hover': {
              '& > fieldset': {
                borderColor: 'primary.main',
              },
            },
          },
        }}
      />
    </Box>
  );
};

export default SearchBar;
