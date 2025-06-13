// Load environment variables FIRST
import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';

// Import middlewares
import { apiLimiter, authLimiter, scholarshipWriteLimiter } from './middleware/rateLimiting';
import { authenticateToken, authorize, optionalAuth } from './middleware/auth';
import { 
  validateScholarship, 
  validateUpdateScholarship, 
  validateLogin, 
  validateCreateUser, 
  handleValidationErrors 
} from './middleware/validation';

// Import controllers
import * as authController from './controllers/authController';
import * as scholarshipController from './controllers/scholarshipController';
import { ScholarshipAgentController } from './controllers/scholarshipAgentController';

// Import services
import { googleSheetsService } from './services/googleSheetsService';

const app = express();
const PORT = process.env.PORT || 5000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: [
    process.env.FRONTEND_URL || 'http://localhost:5173',
    'http://localhost:5176',
    'http://localhost:5174',
    'http://127.0.0.1:5174', // Add this line
    'http://localhost:5175'
  ],
  credentials: true,
}));

// Logging
app.use(morgan('combined'));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
app.use('/api/', apiLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    success: true, 
    message: 'Scholarship Admin API is running',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// AUTHENTICATION ROUTES
// ============================================================================

app.post('/api/auth/login', 
  authLimiter,
  validateLogin,
  handleValidationErrors,
  authController.login
);

app.post('/api/auth/refresh',
  authLimiter,
  authController.refreshToken
);

app.post('/api/auth/logout',
  authenticateToken,
  authController.logout
);

app.get('/api/auth/profile',
  authenticateToken,
  authController.getProfile
);

// User management (admin only)
app.post('/api/auth/users',
  authenticateToken,
  authorize('super_admin'),
  validateCreateUser,
  handleValidationErrors,
  authController.createUser
);

app.get('/api/auth/users',
  authenticateToken,
  authorize('super_admin', 'admin'),
  authController.getUsers
);

app.put('/api/auth/users/:id',
  authenticateToken,
  authorize('super_admin', 'admin'),
  authController.updateUser
);

// ============================================================================
// PUBLIC SCHOLARSHIP ROUTES (for frontend)
// ============================================================================

app.get('/api/public/scholarships',
  scholarshipController.getPublicScholarships
);

app.get('/api/public/categories',
  scholarshipController.getCategories
);

// ============================================================================
// ADMIN SCHOLARSHIP ROUTES
// ============================================================================

// Get scholarships (with admin filters)
app.get('/api/admin/scholarships',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor', 'viewer'),
  scholarshipController.getScholarships
);

// Get scholarship by ID
app.get('/api/admin/scholarships/:id',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor', 'viewer'),
  scholarshipController.getScholarshipById
);

// Create scholarship
app.post('/api/admin/scholarships',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor'),
  scholarshipWriteLimiter,
  validateScholarship,
  handleValidationErrors,
  scholarshipController.createScholarship
);

// Update scholarship
app.put('/api/admin/scholarships/:id',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor'),
  scholarshipWriteLimiter,
  validateUpdateScholarship,
  handleValidationErrors,
  scholarshipController.updateScholarship
);

// Delete scholarship
app.delete('/api/admin/scholarships/:id',
  authenticateToken,
  authorize('super_admin', 'admin'),
  scholarshipController.deleteScholarship
);

// Bulk operations
app.post('/api/admin/scholarships/bulk-update',
  authenticateToken,
  authorize('super_admin', 'admin'),
  scholarshipWriteLimiter,
  scholarshipController.bulkUpdateScholarships
);

// ============================================================================
// ADMIN ANALYTICS ROUTES
// ============================================================================

app.get('/api/admin/analytics',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor', 'viewer'),
  scholarshipController.getAnalytics
);

app.get('/api/admin/categories',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor', 'viewer'),
  scholarshipController.getCategories
);

// ============================================================================
// SCHOLARSHIP AGENT ROUTES (AI-powered discovery)
// ============================================================================

const scholarshipAgentController = new ScholarshipAgentController();

// Get agent status
app.get('/api/admin/agent/status',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor', 'viewer'),
  async (req, res) => {
    try {
      const status = scholarshipAgentController.getAgentStatus();
      res.json({
        success: true,
        data: status
      });
    } catch (error) {
      console.error('Error getting agent status:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get agent status'
      });
    }
  }
);

// Run scholarship discovery
app.post('/api/admin/agent/discover',
  authenticateToken,
  authorize('super_admin', 'admin', 'editor'),
  async (req, res) => {
    try {
      const { searchCriteria } = req.body;
      console.log('Starting scholarship discovery via API...');
      
      const result = await scholarshipAgentController.runDiscovery(searchCriteria);
      
      if (result.success) {
        res.json({
          success: true,
          message: 'Scholarship discovery completed',
          data: {
            scholarships_discovered: result.scholarships_discovered,
            scholarships_saved: result.scholarships_saved
          }
        });
      } else {
        res.status(400).json({
          success: false,
          message: 'Scholarship discovery failed',
          error: result.error
        });
      }
    } catch (error) {
      console.error('Error running scholarship discovery:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to run scholarship discovery'
      });
    }
  }
);

// ============================================================================
// ERROR HANDLING
// ============================================================================

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.originalUrl} not found`
  });
});

// Global error handler
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Global error handler:', error);
  
  res.status(error.statusCode || 500).json({
    success: false,
    message: error.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
  });
});

// ============================================================================
// SERVER INITIALIZATION
// ============================================================================

const startServer = async () => {
  try {
    // Initialize Google Sheets
    console.log('Initializing Google Sheets...');
    await googleSheetsService.initializeSheets();
    console.log('Google Sheets initialized successfully');

    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Scholarship Admin API server running on port ${PORT}`);
      console.log(`📚 API Documentation: http://localhost:${PORT}/health`);
      console.log(`🔒 Environment: ${process.env.NODE_ENV || 'development'}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Start the server
startServer();

export default app;
