import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Button,
  Box,
  Stack,
  Avatar,
} from '@mui/material';
import {
  CalendarMonth as CalendarIcon,
  AttachMoney as MoneyIcon,
  LocationOn as LocationIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import type { Scholarship } from '../../types/scholarship';
import { formatDeadline } from '../../utils/dateUtils';

interface ScholarshipCardProps {
  scholarship: Scholarship;
  onViewDetails: (scholarship: Scholarship) => void;
}

/**
 * Compact scholarship card with consistent dimensions and "View Details" action
 */
const ScholarshipCard: React.FC<ScholarshipCardProps> = ({ 
  scholarship, 
  onViewDetails 
}) => {
  const { text: deadlineText, isUrgent } = formatDeadline(scholarship.deadline);

  const handleViewDetails = () => {
    onViewDetails(scholarship);
  };

  // Generate a color for the provider avatar
  const getProviderColor = (provider: string) => {
    const colors = ['#2563eb', '#7c3aed', '#059669', '#dc2626', '#ea580c'];
    const index = provider.length % colors.length;
    return colors[index];
  };

  return (
    <Card 
      elevation={0}
      sx={{ 
        height: 400, // Reduced height for more compact cards
        width: '100%',
        minWidth: 0,
        maxWidth: '100%',
        display: 'flex', 
        flexDirection: 'column',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        border: '1px solid #e2e8f0',
        borderRadius: 3,
        overflow: 'hidden',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          borderColor: 'primary.main',
        },
      }}
      onClick={handleViewDetails}
    >
      {/* Header with gradient background - Fixed height */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${getProviderColor(scholarship.provider)}15 0%, ${getProviderColor(scholarship.provider)}25 100%)`,
          p: 2.5,
          height: 100, // Reduced header height
          display: 'flex',
          alignItems: 'center',
          width: '100%',
        }}
      >
        <Avatar
          sx={{
            bgcolor: getProviderColor(scholarship.provider),
            width: 40,
            height: 40,
            fontSize: '1rem',
            fontWeight: 600,
            mr: 2,
            flexShrink: 0,
          }}
        >
          {scholarship.provider.charAt(0)}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography 
            variant="h6" 
            component="h3" 
            sx={{ 
              fontWeight: 600, 
              mb: 0.5,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: 1.2,
              fontSize: '1.1rem',
            }}
          >
            {scholarship.title}
          </Typography>
          <Chip 
            label={scholarship.category} 
            size="small" 
            sx={{
              backgroundColor: getProviderColor(scholarship.provider),
              color: 'white',
              fontWeight: 500,
              fontSize: '0.75rem',
            }}
          />
        </Box>
      </Box>

      {/* Content area */}
      <CardContent sx={{ 
        flex: 1, 
        pt: 2, 
        pb: 1, 
        display: 'flex', 
        flexDirection: 'column',
        width: '100%',
      }}>
        {/* Description - Truncated */}
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 2, 
            lineHeight: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 2, // Only 2 lines for compact view
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            height: '3em', // Fixed height for 2 lines
          }}
        >
          {scholarship.description}
        </Typography>

        {/* Key details - Compact version */}
        <Stack spacing={1} sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <MoneyIcon sx={{ fontSize: 18, color: 'success.main' }} />
            <Typography variant="body2" fontWeight="600" color="success.main">
              {scholarship.amount}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <CalendarIcon sx={{ 
              fontSize: 18, 
              color: isUrgent ? 'error.main' : 'primary.main' 
            }} />
            <Typography 
              variant="body2" 
              color={isUrgent ? 'error.main' : 'text.secondary'}
              fontWeight={isUrgent ? 600 : 400}
            >
              {deadlineText}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <LocationIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {scholarship.location}
            </Typography>
          </Box>
        </Stack>

        {/* Eligibility preview - Just show count */}
        {scholarship.eligibility.length > 0 && (
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'flex-end' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckIcon sx={{ fontSize: 16, color: 'success.main' }} />
              <Typography variant="caption" color="text.secondary">
                {scholarship.eligibility.length} eligibility requirement{scholarship.eligibility.length !== 1 ? 's' : ''}
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>

      {/* Actions - Fixed at bottom */}
      <CardActions sx={{ 
        p: 2.5, 
        pt: 0, 
        width: '100%',
        height: 60, // Fixed height for button area
        display: 'flex',
        alignItems: 'center',
      }}>
        <Button
          variant="contained"
          startIcon={<ViewIcon />}
          onClick={handleViewDetails}
          fullWidth
          sx={{ 
            textTransform: 'none',
            py: 1,
            fontWeight: 600,
            borderRadius: 2,
          }}
        >
          View Details
        </Button>
      </CardActions>
    </Card>
  );
};

export default ScholarshipCard;