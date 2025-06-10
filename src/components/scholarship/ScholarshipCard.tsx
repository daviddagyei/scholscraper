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
  Divider,
} from '@mui/material';
import {
  CalendarMonth as CalendarIcon,
  AttachMoney as MoneyIcon,
  LocationOn as LocationIcon,
  School as SchoolIcon,
  OpenInNew as LinkIcon,
} from '@mui/icons-material';
import type { Scholarship } from '../../types/scholarship';
import { formatDeadline } from '../../utils/dateUtils';

interface ScholarshipCardProps {
  scholarship: Scholarship;
}

/**
 * Card component for displaying individual scholarship information
 */
const ScholarshipCard: React.FC<ScholarshipCardProps> = ({ scholarship }) => {
  const { text: deadlineText, isUrgent } = formatDeadline(scholarship.deadline);

  const handleApplyClick = () => {
    if (scholarship.applicationUrl) {
      window.open(scholarship.applicationUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card 
      elevation={2} 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Header with title and category */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" component="h3" gutterBottom>
            {scholarship.title}
          </Typography>
          <Chip 
            label={scholarship.category} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
        </Box>

        {/* Description */}
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ mb: 2, lineHeight: 1.5 }}
        >
          {scholarship.description.length > 150 
            ? `${scholarship.description.substring(0, 150)}...`
            : scholarship.description
          }
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* Key details */}
        <Stack spacing={1.5}>
          {/* Amount */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <MoneyIcon color="success" fontSize="small" />
            <Typography variant="body2" fontWeight="medium">
              {scholarship.amount}
            </Typography>
          </Box>

          {/* Deadline */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarIcon 
              color={isUrgent ? 'error' : 'primary'} 
              fontSize="small" 
            />
            <Typography 
              variant="body2" 
              color={isUrgent ? 'error.main' : 'text.primary'}
              fontWeight={isUrgent ? 'medium' : 'normal'}
            >
              {deadlineText}
            </Typography>
          </Box>

          {/* Provider */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SchoolIcon color="primary" fontSize="small" />
            <Typography variant="body2">
              {scholarship.provider}
            </Typography>
          </Box>

          {/* Location */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LocationIcon color="secondary" fontSize="small" />
            <Typography variant="body2">
              {scholarship.location}
            </Typography>
          </Box>
        </Stack>

        {/* Eligibility chips */}
        {scholarship.eligibility.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              Eligibility:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {scholarship.eligibility.slice(0, 3).map((criteria, index) => (
                <Chip
                  key={index}
                  label={criteria}
                  size="small"
                  variant="outlined"
                  color="secondary"
                />
              ))}
              {scholarship.eligibility.length > 3 && (
                <Chip
                  label={`+${scholarship.eligibility.length - 3} more`}
                  size="small"
                  variant="outlined"
                  color="secondary"
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<LinkIcon />}
          onClick={handleApplyClick}
          disabled={!scholarship.applicationUrl}
          fullWidth
          sx={{ textTransform: 'none' }}
        >
          {scholarship.applicationUrl ? 'Apply Now' : 'Application Unavailable'}
        </Button>
      </CardActions>
    </Card>
  );
};

export default ScholarshipCard;