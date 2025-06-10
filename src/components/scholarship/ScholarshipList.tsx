import React from 'react';
import {
  Grid,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import { Scholarship } from '../../types/scholarship';
import ScholarshipCard from './ScholarshipCard';

interface ScholarshipListProps {
  scholarships: Scholarship[];
  isLoading?: boolean;
  error?: string | null;
  searchStats?: {
    totalScholarships: number;
    filteredCount: number;
    hasActiveFilters: boolean;
  };
}

/**
 * Component for displaying a list of scholarships in a grid layout
 */
const ScholarshipList: React.FC<ScholarshipListProps> = ({
  scholarships,
  isLoading = false,
  error = null,
  searchStats,
}) => {
  // Loading state
  if (isLoading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: 300 
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Error Loading Scholarships
        </Typography>
        <Typography variant="body2">
          {error}
        </Typography>
      </Alert>
    );
  }

  // Empty state
  if (scholarships.length === 0) {
    return (
      <Paper 
        elevation={1} 
        sx={{ 
          p: 4, 
          textAlign: 'center',
          backgroundColor: '#fafafa'
        }}
      >
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {searchStats?.hasActiveFilters 
            ? 'No scholarships match your search criteria'
            : 'No scholarships available'
          }
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {searchStats?.hasActiveFilters
            ? 'Try adjusting your filters or search terms'
            : 'Check back later for new opportunities'
          }
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Search results summary */}
      {searchStats && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" color="text.secondary">
            Showing {scholarships.length} of {searchStats.totalScholarships} scholarships
            {searchStats.hasActiveFilters && (
              <Typography 
                component="span" 
                variant="body2" 
                color="primary" 
                sx={{ ml: 1 }}
              >
                (filtered)
              </Typography>
            )}
          </Typography>
        </Box>
      )}

      {/* Scholarship grid */}
      <Grid container spacing={3}>
        {scholarships.map((scholarship) => (
          <Grid item xs={12} sm={6} lg={4} key={scholarship.id}>
            <ScholarshipCard scholarship={scholarship} />
          </Grid>
        ))}
      </Grid>

      {/* Additional info for large result sets */}
      {scholarships.length > 12 && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing all {scholarships.length} results. 
            Use filters to narrow down your search.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ScholarshipList;
