import React from 'react';
import {
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Box,
  Typography,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import type { SearchFilters } from '../../types/scholarship';

interface FilterControlsProps {
  filters: SearchFilters;
  onFiltersChange: (filters: Partial<SearchFilters>) => void;
  onReset: () => void;
  filterOptions: {
    categories: string[];
    eligibilityOptions: string[];
  };
  isCompact?: boolean;
}

/**
 * Advanced filter controls for scholarship search
 */
const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onReset,
  filterOptions,
  isCompact = false,
}) => {
  const hasActiveFilters = 
    filters.category !== '' ||
    filters.minAmount > 0 ||
    filters.maxAmount < 100000 ||
    filters.deadlineFrom !== null ||
    filters.deadlineTo !== null ||
    filters.eligibility.length > 0;

  const FilterContent = () => (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {/* Category Filter */}
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <FormControl fullWidth size="small">
            <InputLabel>Category</InputLabel>
            <Select
              value={filters.category}
              label="Category"
              onChange={(e) => onFiltersChange({ category: e.target.value })}
            >
              <MenuItem value="">All Categories</MenuItem>
              {filterOptions.categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Amount Range */}
        <Box sx={{ flex: '1 1 150px', minWidth: '150px' }}>
          <TextField
            fullWidth
            size="small"
            label="Min Amount ($)"
            type="number"
            value={filters.minAmount || ''}
            onChange={(e) => onFiltersChange({ minAmount: Number(e.target.value) || 0 })}
            inputProps={{ min: 0 }}
          />
        </Box>

        <Box sx={{ flex: '1 1 150px', minWidth: '150px' }}>
          <TextField
            fullWidth
            size="small"
            label="Max Amount ($)"
            type="number"
            value={filters.maxAmount === 100000 ? '' : filters.maxAmount}
            onChange={(e) => onFiltersChange({ maxAmount: Number(e.target.value) || 100000 })}
            inputProps={{ min: 0 }}
          />
        </Box>

        {/* Date Range */}
        <Box sx={{ flex: '1 1 180px', minWidth: '180px' }}>
          <DatePicker
            label="Deadline From"
            value={filters.deadlineFrom}
            onChange={(date) => onFiltersChange({ deadlineFrom: date })}
            slotProps={{
              textField: {
                size: 'small',
                fullWidth: true,
              },
            }}
          />
        </Box>

        <Box sx={{ flex: '1 1 180px', minWidth: '180px' }}>
          <DatePicker
            label="Deadline To"
            value={filters.deadlineTo}
            onChange={(date) => onFiltersChange({ deadlineTo: date })}
            slotProps={{
              textField: {
                size: 'small',
                fullWidth: true,
              },
            }}
          />
        </Box>

        {/* Eligibility Filter */}
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <FormControl fullWidth size="small">
            <InputLabel>Eligibility</InputLabel>
            <Select
              multiple
              value={filters.eligibility}
              label="Eligibility"
              onChange={(e) => onFiltersChange({ 
                eligibility: typeof e.target.value === 'string' 
                  ? [e.target.value] 
                  : e.target.value 
              })}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {filterOptions.eligibilityOptions.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Reset Button */}
        <Box sx={{ flex: '1 1 200px', minWidth: '200px', display: 'flex', alignItems: 'center' }}>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<ClearIcon />}
            onClick={onReset}
            disabled={!hasActiveFilters}
            sx={{ textTransform: 'none' }}
          >
            Reset Filters
          </Button>
          {hasActiveFilters && (
            <Typography variant="caption" color="primary" sx={{ ml: 2 }}>
              Active
            </Typography>
          )}
        </Box>
      </Box>
    </LocalizationProvider>
  );

  if (isCompact) {
    return (
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="filter-content"
            id="filter-header"
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterIcon color="primary" />
              <Typography variant="subtitle1">
                Advanced Filters
              </Typography>
              {hasActiveFilters && (
                <Chip 
                  label="Active" 
                  size="small" 
                  color="primary" 
                  variant="outlined" 
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <FilterContent />
          </AccordionDetails>
        </Accordion>
      </Paper>
    );
  }

  return (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <FilterIcon color="primary" />
        <Typography variant="h6">
          Filters
        </Typography>
        {hasActiveFilters && (
          <Chip 
            label="Active" 
            size="small" 
            color="primary" 
          />
        )}
      </Box>
      <Divider sx={{ mb: 2 }} />
      <FilterContent />
    </Paper>
  );
};

export default FilterControls;