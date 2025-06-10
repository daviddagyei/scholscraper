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
  Avatar,
} from '@mui/material';
import {
  CalendarMonth as CalendarIcon,
  AttachMoney as MoneyIcon,
  LocationOn as LocationIcon,
  School as SchoolIcon,
  OpenInNew as LinkIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import type { Scholarship } from '../../types/scholarship';
import { formatDeadline } from '../../utils/dateUtils';

interface ScholarshipCardProps {
  scholarship: Scholarship;
}

/**
 * Modern scholarship card with enhanced visual design
 */
const ScholarshipCard: React.FC<ScholarshipCardProps> = ({ scholarship }) => {
  const { text: deadlineText, isUrgent } = formatDeadline(scholarship.deadline);

  const handleApplyClick = () => {
    if (scholarship.applicationUrl) {
      window.open(scholarship.applicationUrl, '_blank', 'noopener,noreferrer');
    }
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
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        border: '1px solid #e2e8f0',
        borderRadius: 3,
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          borderColor: 'primary.main',
        },
      }}
    >
      {/* Header with gradient background */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${getProviderColor(scholarship.provider)}15 0%, ${getProviderColor(scholarship.provider)}25 100%)`,
          p: 3,
          pb: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: getProviderColor(scholarship.provider),
              width: 48,
              height: 48,
              fontSize: '1.2rem',
              fontWeight: 600,
            }}
          >
            {scholarship.provider.charAt(0)}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 600, mb: 1 }}>
              {scholarship.title}
            </Typography>
            <Chip 
              label={scholarship.category} 
              size="small" 
              sx={{
                backgroundColor: getProviderColor(scholarship.provider),
                color: 'white',
                fontWeight: 500,
              }}
            />
          </Box>
        </Box>
      </Box>

      <CardContent sx={{ flexGrow: 1, pt: 0 }}>
        {/* Description */}
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 3, 
            lineHeight: 1.6,
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {scholarship.description}
        </Typography>

        {/* Key details with modern icons */}
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: 1,
                backgroundColor: 'success.light',
                color: 'success.contrastText',
              }}
            >
              <MoneyIcon fontSize="small" />
            </Box>
            <Typography variant="body1" fontWeight="600" color="success.main">
              {scholarship.amount}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: 1,
                backgroundColor: isUrgent ? 'error.light' : 'primary.light',
                color: isUrgent ? 'error.contrastText' : 'primary.contrastText',
              }}
            >
              <CalendarIcon fontSize="small" />
            </Box>
            <Typography 
              variant="body2" 
              color={isUrgent ? 'error.main' : 'text.primary'}
              fontWeight={isUrgent ? 600 : 400}
            >
              {deadlineText}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: 1,
                backgroundColor: 'grey.100',
                color: 'text.primary',
              }}
            >
              <SchoolIcon fontSize="small" />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {scholarship.provider}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 32,
                height: 32,
                borderRadius: 1,
                backgroundColor: 'secondary.light',
                color: 'secondary.contrastText',
              }}
            >
              <LocationIcon fontSize="small" />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {scholarship.location}
            </Typography>
          </Box>
        </Stack>

        {/* Eligibility chips */}
        {scholarship.eligibility.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block" sx={{ mb: 1 }}>
              Eligibility Requirements:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {scholarship.eligibility.slice(0, 2).map((criteria, index) => (
                <Chip
                  key={index}
                  label={criteria}
                  size="small"
                  icon={<CheckIcon sx={{ fontSize: 16 }} />}
                  variant="outlined"
                  sx={{
                    borderColor: 'success.main',
                    color: 'success.main',
                    '& .MuiChip-icon': {
                      color: 'success.main',
                    },
                  }}
                />
              ))}
              {scholarship.eligibility.length > 2 && (
                <Chip
                  label={`+${scholarship.eligibility.length - 2} more`}
                  size="small"
                  variant="outlined"
                  sx={{ color: 'text.secondary' }}
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ p: 3, pt: 0 }}>
        <Button
          variant="contained"
          startIcon={<LinkIcon />}
          onClick={handleApplyClick}
          disabled={!scholarship.applicationUrl}
          fullWidth
          sx={{ 
            textTransform: 'none',
            py: 1.5,
            fontWeight: 600,
            borderRadius: 2,
          }}
        >
          {scholarship.applicationUrl ? 'Apply Now' : 'Application Unavailable'}
        </Button>
      </CardActions>
    </Card>
  );
};

export default ScholarshipCard;