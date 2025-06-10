import React, { useState } from 'react';
import {
  Grid,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import type { Scholarship } from '../../types/scholarship';
import ScholarshipCard from './ScholarshipCard';
import ScholarshipModal from './ScholarshipModal';

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
 * Component for displaying scholarships with modal details view
 */
const ScholarshipList: React.FC<ScholarshipListProps> = ({
  scholarships,
  isLoading = false,
  error = null,
  searchStats,
}) => {
  const [selectedScholarship, setSelectedScholarship] = useState<Scholarship | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleViewDetails = (scholarship: Scholarship) => {
    setSelectedScholarship(scholarship);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedScholarship(null);
  };

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

      {/* Scholarship grid with consistent card sizes */}
      <Grid 
        container 
        spacing={3}
        sx={{
          '& .MuiGrid-item': {
            display: 'flex',
            width: '100%',
          }
        }}
      >
        {scholarships.map((scholarship) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            lg={4} 
            key={scholarship.id}
            sx={{
              display: 'flex !important',
              width: '100%',
              maxWidth: {
                xs: '100%',
                sm: 'calc(50% - 12px)',
                lg: 'calc(33.333% - 16px)',
              },
              flexBasis: {
                xs: '100%',
                sm: 'calc(50% - 12px)',
                lg: 'calc(33.333% - 16px)',
              },
            }}
          >
            <ScholarshipCard 
              scholarship={scholarship} 
              onViewDetails={handleViewDetails}
            />
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

      {/* Scholarship Detail Modal */}
      <ScholarshipModal
        scholarship={selectedScholarship}
        open={modalOpen}
        onClose={handleCloseModal}
      />
    </Box>
  );
};

export default ScholarshipList