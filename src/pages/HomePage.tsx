import React from 'react';
import {
  Box,
  Typography,
  Alert,
  Button,
  Stack,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import Layout from '../components/common/Layout';
import SearchBar from '../components/scholarship/SearchBar';
import FilterControls from '../components/scholarship/FilterControls';
import ScholarshipList from '../components/scholarship/ScholarshipList';
import { useScholarships } from '../hooks/useScholarships';
import { useSearch } from '../hooks/useSearch';

/**
 * Main home page component that brings together all scholarship functionality
 */
const HomePage: React.FC = () => {
  const { 
    scholarships, 
    isLoading, 
    error, 
    refreshScholarships 
  } = useScholarships();
  
  const {
    filters,
    updateFilters,
    resetFilters,
    filteredScholarships,
    filterOptions,
    searchStats,
  } = useSearch(scholarships);

  return (
    <Layout title="Scholarship Database">
      <Box>
        {/* Header Section */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Find Your Perfect Scholarship
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
            Discover funding opportunities for your education. Search through our comprehensive 
            database of scholarships, grants, and financial aid programs.
          </Typography>
          
          {/* Info alert for users */}
          <Alert 
            severity="info" 
            icon={<InfoIcon />}
            sx={{ mb: 3, maxWidth: 800, mx: 'auto' }}
          >
            <Typography variant="body2">
              💡 <strong>Pro Tip:</strong> Use the search bar for quick results, or expand the 
              advanced filters to narrow down scholarships by category, location, amount, and deadlines.
            </Typography>
          </Alert>
        </Box>

        {/* Search Bar */}
        <SearchBar
          searchTerm={filters.searchTerm}
          onSearchChange={(searchTerm) => updateFilters({ searchTerm })}
        />

        {/* Filter Controls */}
        <FilterControls
          filters={filters}
          onFiltersChange={updateFilters}
          onReset={resetFilters}
          filterOptions={filterOptions}
          isCompact={true}
        />

        {/* Error State with Retry */}
        {error && (
          <Box sx={{ mb: 3 }}>
            <Alert 
              severity="error" 
              action={
                <Button 
                  color="inherit" 
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={refreshScholarships}
                >
                  Retry
                </Button>
              }
            >
              <Typography variant="subtitle2" gutterBottom>
                Failed to load scholarships
              </Typography>
              <Typography variant="body2">
                {error}
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Quick Stats */}
        {!isLoading && !error && scholarships.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Stack 
              direction={{ xs: 'column', sm: 'row' }} 
              spacing={2} 
              justifyContent="space-between"
              alignItems={{ xs: 'stretch', sm: 'center' }}
            >
              <Typography variant="body1" color="text.secondary">
                {searchStats.hasActiveFilters
                  ? `Found ${filteredScholarships.length} scholarships matching your criteria`
                  : `Browse ${scholarships.length} available scholarships`
                }
              </Typography>
              
              {!isLoading && (
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={refreshScholarships}
                  size="small"
                  sx={{ textTransform: 'none' }}
                >
                  Refresh Data
                </Button>
              )}
            </Stack>
          </Box>
        )}

        {/* Scholarship List */}
        <ScholarshipList
          scholarships={filteredScholarships}
          isLoading={isLoading}
          error={error}
          searchStats={searchStats}
        />

        {/* Footer Info */}
        {!isLoading && !error && scholarships.length > 0 && (
          <Box sx={{ mt: 6, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Data is updated regularly. Always verify scholarship details and deadlines 
              on the provider's official website before applying.
            </Typography>
          </Box>
        )}
      </Box>
    </Layout>
  );
};

export default HomePage;
