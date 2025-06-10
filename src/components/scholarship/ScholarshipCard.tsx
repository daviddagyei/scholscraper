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
 * Modern scholarship card with consistent dimensions and button positioning
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
        height: 520, // Fixed height for consistency
        width: '100%', // Ensure full width within container
        minWidth: 0, // Allow shrinking
        maxWidth: '100%', // Prevent overflow
        display: 'flex', 
        flexDirection: 'column',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        border: '1px solid #e2e8f0',
        borderRadius: 3,
        overflow: 'hidden',
        flex: 1, // Take full available space
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          borderColor: 'primary.main',
        },
      }}
    >
      {/* Header with gradient background - Fixed height */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${getProviderColor(scholarship.provider)}15 0%, ${getProviderColor(scholarship.provider)}25 100%)`,
          p: 3,
          pb: 2,
          height: 120, // Fixed height instead of minHeight
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2, width: '100%' }}>
          <Avatar
            sx={{
              bgcolor: getProviderColor(scholarship.provider),
              width: 48,
              height: 48,
              fontSize: '1.2rem',
              fontWeight: 600,
              flexShrink: 0,
            }}
          >
            {scholarship.provider.charAt(0)}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0, width: '100%' }}>
            <Typography 
              variant="h6" 
              component="h3" 
              sx={{ 
                fontWeight: 600, 
                mb: 1,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                lineHeight: 1.3,
                width: '100%',
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
              }}
            />
          </Box>
        </Box>
      </Box>

      {/* Content area - This will expand to fill available space */}
      <Box sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        width: '100%',
        minWidth: 0,
      }}>
        <CardContent sx={{ 
          flexGrow: 1, 
          pt: 2, 
          pb: 1, 
          display: 'flex', 
          flexDirection: 'column',
          width: '100%',
          minWidth: 0,
        }}>
          {/* Description - Fixed height with overflow handling */}
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
              height: '4.8em', // Fixed height for 3 lines
              width: '100%',
            }}
          >
            {scholarship.description}
          </Typography>

          {/* Key details with modern icons - Fixed spacing */}
          <Stack spacing={1.5} sx={{ mb: 2, width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
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
                  flexShrink: 0,
                }}
              >
                <MoneyIcon fontSize="small" />
              </Box>
              <Typography variant="body1" fontWeight="600" color="success.main" sx={{ minWidth: 0 }}>
                {scholarship.amount}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
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
                  flexShrink: 0,
                }}
              >
                <CalendarIcon fontSize="small" />
              </Box>
              <Typography 
                variant="body2" 
                color={isUrgent ? 'error.main' : 'text.primary'}
                fontWeight={isUrgent ? 600 : 400}
                sx={{ minWidth: 0 }}
              >
                {deadlineText}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
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
                  flexShrink: 0,
                }}
              >
                <SchoolIcon fontSize="small" />
              </Box>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  minWidth: 0,
                  flex: 1,
                }}
              >
                {scholarship.provider}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
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
                  flexShrink: 0,
                }}
              >
                <LocationIcon fontSize="small" />
              </Box>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  minWidth: 0,
                  flex: 1,
                }}
              >
                {scholarship.location}
              </Typography>
            </Box>
          </Stack>

          {/* Eligibility chips - This section will expand to fill remaining space */}
          <Box sx={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'flex-start',
            minHeight: 60, 
            width: '100%' 
          }}>
            {scholarship.eligibility.length > 0 && (
              <>
                <Typography variant="caption" color="text.secondary" gutterBottom display="block" sx={{ mb: 1 }}>
                  Eligibility:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, width: '100%' }}>
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
                        fontSize: '0.75rem',
                        maxWidth: 'calc(50% - 4px)',
                        '& .MuiChip-label': {
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        },
                      }}
                    />
                  ))}
                  {scholarship.eligibility.length > 2 && (
                    <Chip
                      label={`+${scholarship.eligibility.length - 2}`}
                      size="small"
                      variant="outlined"
                      sx={{ 
                        color: 'text.secondary',
                        fontSize: '0.75rem',
                      }}
                    />
                  )}
                </Box>
              </>
            )}
          </Box>
        </CardContent>

        {/* Actions - Fixed at bottom with consistent height */}
        <CardActions sx={{ 
          p: 3, 
          pt: 0, 
          width: '100%',
          height: 72, // Fixed height for button area
          display: 'flex',
          alignItems: 'center',
        }}>
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
              width: '100%',
            }}
          >
            {scholarship.applicationUrl ? 'Apply Now' : 'Application Unavailable'}
          </Button>
        </CardActions>
      </Box>
    </Card>
  );
};

export default ScholarshipCard;