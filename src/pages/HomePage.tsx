import React from 'react';
import {
  Box,
  Typography,
  Alert,
  Button,
  Stack,
  Paper,
  Fade,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import Layout from '../components/common/Layout';
import SearchBar from '../components/scholarship/SearchBar';
import FilterControls from '../components/scholarship/FilterControls';
import ScholarshipList from '../components/scholarship/ScholarshipList';
import { useScholarships } from '../hooks/useScholarships';
import { useSearch } from '../hooks/useSearch';

/**
 * Main home page component with modern design and improved UX
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

  // Calculate total scholarship value for display
  const totalValue = scholarships.reduce((sum, scholarship) => {
    const amount = scholarship.amount.replace(/[$,\s]/g, '');
    const num = parseFloat(amount);
    return sum + (isNaN(num) ? 0 : num);
  }, 0);

  return (
    <Layout title="Scholarship Database">
      <Box>
        {/* Hero Section */}
        <Fade in timeout={800}>
          <Box sx={{ mb: { xs: 4, md: 6 }, textAlign: 'center' }}>
            <Typography 
              variant="h1" 
              component="h1" 
              sx={{ 
                mb: 3,
                fontSize: { xs: '2.5rem', sm: '3rem', md: '3.5rem' },
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 700,
              }}
            >
              Find Your Perfect Scholarship
            </Typography>
            
            <Typography 
              variant="h5" 
              color="text.secondary" 
              sx={{ 
                mb: 4, 
                maxWidth: 700, 
                mx: 'auto',
                fontWeight: 400,
                lineHeight: 1.6,
              }}
            >
              Discover funding opportunities for your education. Search through our comprehensive 
              database of scholarships, grants, and financial aid programs.
            </Typography>            {/* Stats Cards */}
            {!isLoading && scholarships.length > 0 && (
              <Box 
                sx={{ 
                  mb: 4, 
                  maxWidth: 800, 
                  mx: 'auto',
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
                  gap: 3,
                }}
              >
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                    border: '1px solid #bae6fd',
                  }}
                >
                  <SchoolIcon sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h4" fontWeight="bold" color="primary.main">
                    {scholarships.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Scholarships Available
                  </Typography>
                </Paper>
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                    border: '1px solid #bbf7d0',
                  }}
                >
                  <MoneyIcon sx={{ fontSize: 32, color: 'success.main', mb: 1 }} />
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    ${(totalValue / 1000).toFixed(0)}K+
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Value Available
                  </Typography>
                </Paper>
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #fefce8 0%, #fef3c7 100%)',
                    border: '1px solid #fde68a',
                  }}
                >
                  <TrendingUpIcon sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {filterOptions.categories.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Categories
                  </Typography>
                </Paper>
              </Box>
            )}
            
            {/* Info Alert */}
            <Alert 
              severity="info" 
              icon={<InfoIcon />}
              sx={{ 
                mb: 4, 
                maxWidth: 900, 
                mx: 'auto',
                borderRadius: 2,
                '& .MuiAlert-message': {
                  fontSize: '0.95rem',
                },
              }}
            >
              <Typography variant="body2">
                💡 <strong>Pro Tip:</strong> Use the search bar for quick results, or expand the 
                advanced filters to narrow down scholarships by category, location, amount, and deadlines.
              </Typography>
            </Alert>
          </Box>
        </Fade>

        {/* Search Section */}
        <Fade in timeout={1000}>
          <Box sx={{ mb: 4 }}>
            <SearchBar
              searchTerm={filters.searchTerm}
              onSearchChange={(searchTerm) => updateFilters({ searchTerm })}
            />
          </Box>
        </Fade>

        {/* Filter Controls */}
        <Fade in timeout={1200}>
          <Box sx={{ mb: 4 }}>
            <FilterControls
              filters={filters}
              onFiltersChange={updateFilters}
              onReset={resetFilters}
              filterOptions={filterOptions}
              isCompact={true}
            />
          </Box>
        </Fade>

        {/* Error State with Retry */}
        {error && (
          <Fade in>
            <Box sx={{ mb: 4 }}>
              <Alert 
                severity="error" 
                sx={{ borderRadius: 2 }}
                action={
                  <Button 
                    color="inherit" 
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={refreshScholarships}
                    sx={{ textTransform: 'none' }}
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
          </Fade>
        )}

        {/* Quick Stats */}
        {!isLoading && !error && scholarships.length > 0 && (
          <Fade in timeout={1400}>
            <Box sx={{ mb: 4 }}>
              <Paper 
                elevation={0}
                sx={{ 
                  p: 3,
                  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                  border: '1px solid #e2e8f0',
                }}
              >
                <Stack 
                  direction={{ xs: 'column', sm: 'row' }} 
                  spacing={3} 
                  justifyContent="space-between"
                  alignItems={{ xs: 'stretch', sm: 'center' }}
                >
                  <Box>
                    <Typography variant="h6" color="text.primary" gutterBottom>
                      {searchStats.hasActiveFilters
                        ? `Found ${filteredScholarships.length} scholarships matching your criteria`
                        : `Browse ${scholarships.length} available scholarships`
                      }
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchStats.hasActiveFilters && (
                        `Filtered from ${scholarships.length} total scholarships`
                      )}
                    </Typography>
                  </Box>
                  
                  {!isLoading && (
                    <Button
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={refreshScholarships}
                      sx={{ 
                        textTransform: 'none',
                        borderRadius: 2,
                        px: 3,
                      }}
                    >
                      Refresh Data
                    </Button>
                  )}
                </Stack>
              </Paper>
            </Box>
          </Fade>
        )}

        {/* Scholarship List */}
        <Fade in timeout={1600}>
          <Box>
            <ScholarshipList
              scholarships={filteredScholarships}
              isLoading={isLoading}
              error={error}
              searchStats={searchStats}
            />
          </Box>
        </Fade>

        {/* Footer Info */}
        {!isLoading && !error && scholarships.length > 0 && (
          <Fade in timeout={1800}>
            <Box sx={{ mt: 8, textAlign: 'center' }}>
              <Paper 
                elevation={0}
                sx={{ 
                  p: 4,
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                  border: '1px solid #e2e8f0',
                }}
              >
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  📚 <strong>Important:</strong> Data is updated regularly. Always verify scholarship details and deadlines 
                  on the provider's official website before applying.
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Need help? Contact our support team or check our FAQ section.
                </Typography>
              </Paper>
            </Box>
          </Fade>
        )}
      </Box>
    </Layout>
  );
};

export default HomePage;