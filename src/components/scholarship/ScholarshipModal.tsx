import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  Stack,
  Chip,
  Divider,
  IconButton,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Close as CloseIcon,
  CalendarMonth as CalendarIcon,
  AttachMoney as MoneyIcon,
  LocationOn as LocationIcon,
  School as SchoolIcon,
  OpenInNew as LinkIcon,
  CheckCircle as CheckIcon,
  Assignment as RequirementIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import type { Scholarship } from '../../types/scholarship';
import { formatDeadline, formatDate } from '../../utils/dateUtils';

interface ScholarshipModalProps {
  scholarship: Scholarship | null;
  open: boolean;
  onClose: () => void;
}

/**
 * Modal component for displaying full scholarship details
 */
const ScholarshipModal: React.FC<ScholarshipModalProps> = ({
  scholarship,
  open,
  onClose,
}) => {
  if (!scholarship) return null;

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
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '90vh',
        },
      }}
    >
      {/* Header */}
      <DialogTitle sx={{ p: 0 }}>
        <Box
          sx={{
            background: `linear-gradient(135deg, ${getProviderColor(scholarship.provider)}15 0%, ${getProviderColor(scholarship.provider)}25 100%)`,
            p: 3,
            position: 'relative',
          }}
        >
          <IconButton
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 16,
              top: 16,
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 1)',
              },
            }}
          >
            <CloseIcon />
          </IconButton>

          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3, pr: 6 }}>
            <Avatar
              sx={{
                bgcolor: getProviderColor(scholarship.provider),
                width: 64,
                height: 64,
                fontSize: '1.5rem',
                fontWeight: 600,
              }}
            >
              {scholarship.provider.charAt(0)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
                {scholarship.title}
              </Typography>
              <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                <Chip 
                  label={scholarship.category} 
                  sx={{
                    backgroundColor: getProviderColor(scholarship.provider),
                    color: 'white',
                    fontWeight: 500,
                  }}
                />
                {scholarship.isActive && (
                  <Chip 
                    label="Active" 
                    color="success" 
                    variant="outlined"
                    size="small"
                  />
                )}
              </Stack>
              <Typography variant="h5" color="success.main" fontWeight="600">
                {scholarship.amount}
              </Typography>
            </Box>
          </Box>
        </Box>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3 }}>
          {/* Description */}
          <Paper elevation={0} sx={{ p: 3, mb: 3, backgroundColor: 'grey.50' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <InfoIcon color="primary" />
              <Typography variant="h6" fontWeight="600">
                About This Scholarship
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ lineHeight: 1.7 }}>
              {scholarship.description}
            </Typography>
          </Paper>

          {/* Key Details */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="600" sx={{ mb: 2 }}>
              Key Details
            </Typography>
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    backgroundColor: isUrgent ? 'error.light' : 'primary.light',
                    color: isUrgent ? 'error.contrastText' : 'primary.contrastText',
                  }}
                >
                  <CalendarIcon />
                </Box>
                <Box>
                  <Typography variant="body1" fontWeight="600">
                    Application Deadline
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color={isUrgent ? 'error.main' : 'text.secondary'}
                    fontWeight={isUrgent ? 600 : 400}
                  >
                    {formatDate(scholarship.deadline)} ({deadlineText})
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    backgroundColor: 'grey.100',
                    color: 'text.primary',
                  }}
                >
                  <SchoolIcon />
                </Box>
                <Box>
                  <Typography variant="body1" fontWeight="600">
                    Provider
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {scholarship.provider}
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    backgroundColor: 'secondary.light',
                    color: 'secondary.contrastText',
                  }}
                >
                  <LocationIcon />
                </Box>
                <Box>
                  <Typography variant="body1" fontWeight="600">
                    Location
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {scholarship.location}
                  </Typography>
                </Box>
              </Box>
            </Stack>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Eligibility Requirements */}
          {scholarship.eligibility.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600" sx={{ mb: 2 }}>
                Eligibility Requirements
              </Typography>
              <List dense>
                {scholarship.eligibility.map((criteria, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={criteria}
                      primaryTypographyProps={{
                        variant: 'body2',
                        color: 'text.primary',
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Application Requirements */}
          {scholarship.requirements.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="600" sx={{ mb: 2 }}>
                Application Requirements
              </Typography>
              <List dense>
                {scholarship.requirements.map((requirement, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <RequirementIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={requirement}
                      primaryTypographyProps={{
                        variant: 'body2',
                        color: 'text.primary',
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </DialogContent>

      {/* Actions */}
      <DialogActions sx={{ p: 3, pt: 0 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          sx={{ textTransform: 'none', px: 3 }}
        >
          Close
        </Button>
        <Button
          variant="contained"
          startIcon={<LinkIcon />}
          onClick={handleApplyClick}
          disabled={!scholarship.applicationUrl}
          sx={{ 
            textTransform: 'none',
            px: 3,
            fontWeight: 600,
          }}
        >
          {scholarship.applicationUrl ? 'Apply Now' : 'Application Unavailable'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ScholarshipModal;