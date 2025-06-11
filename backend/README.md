# Scholarship Admin Backend

Administrative backend API for managing scholarships with Google Sheets integration.

## 🚀 Features

- **RESTful API** for scholarship management
- **Google Sheets Integration** for data storage
- **JWT Authentication** with role-based access control
- **Rate Limiting** for API protection
- **Input Validation** and sanitization
- **Audit Logging** for all operations
- **Analytics** and reporting endpoints

## 🏗️ Architecture

- **Express.js** with TypeScript
- **Google Sheets API** for data persistence
- **JWT** for authentication
- **bcryptjs** for password hashing
- **express-validator** for input validation
- **helmet** for security headers
- **morgan** for request logging

## 🔧 Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:

```env
# Server Configuration
NODE_ENV=development
PORT=5000

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_EXPIRES_IN=7d

# Google Sheets Configuration
GOOGLE_SHEETS_ID=your-google-sheets-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----"

# CORS Configuration
FRONTEND_URL=http://localhost:5173

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Admin Configuration
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=admin123
```

### 3. Google Sheets Setup

1. Create a new Google Sheets document
2. Create a Google Cloud Project and enable the Sheets API
3. Create a service account and download the JSON credentials
4. Share your Google Sheets with the service account email
5. Add the credentials to your `.env` file

### 4. Run the Server

```bash
# Development mode with hot reload
npm run dev

# Production build
npm run build
npm start
```

## 📊 Google Sheets Structure

The backend expects three sheets in your Google Sheets document:

### Scholarships Sheet
| Column | Description |
|--------|-------------|
| ID | Unique identifier |
| Title | Scholarship title |
| Description | Detailed description |
| Amount | Award amount |
| Deadline | Application deadline (YYYY-MM-DD) |
| Eligibility | Comma-separated eligibility criteria |
| Requirements | Comma-separated requirements |
| Application URL | Link to application |
| Provider | Organization providing the scholarship |
| Category | Scholarship category |
| Status | active/inactive/draft |
| Created Date | When created (ISO string) |
| Modified Date | Last modified (ISO string) |
| Created By | Email of creator |
| Last Modified By | Email of last modifier |

### AuditLog Sheet
| Column | Description |
|--------|-------------|
| Timestamp | When the action occurred |
| Action | Type of action (created/updated/deleted/etc.) |
| Scholarship ID | ID of affected scholarship |
| User Email | Email of user who performed action |
| Changes Made | Description of changes |
| Previous Values | JSON of previous values |
| IP Address | User's IP address |

### Categories Sheet
| Column | Description |
|--------|-------------|
| Category Name | Name of the category |
| Description | Category description |
| Color Code | Hex color for UI |
| Active Status | Whether category is active |

## 🔐 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get current user profile
- `POST /api/auth/users` - Create new user (super_admin only)
- `GET /api/auth/users` - Get all users (admin+)
- `PUT /api/auth/users/:id` - Update user (admin+)

### Public Endpoints (for frontend)
- `GET /api/public/scholarships` - Get active scholarships
- `GET /api/public/categories` - Get available categories

### Admin Endpoints
- `GET /api/admin/scholarships` - Get scholarships with filters
- `GET /api/admin/scholarships/:id` - Get scholarship by ID
- `POST /api/admin/scholarships` - Create new scholarship
- `PUT /api/admin/scholarships/:id` - Update scholarship
- `DELETE /api/admin/scholarships/:id` - Delete scholarship
- `POST /api/admin/scholarships/bulk-update` - Bulk update scholarships
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/categories` - Get categories

## 👥 User Roles

- **super_admin**: Full access to all features including user management
- **admin**: Can manage scholarships and view analytics
- **editor**: Can create and edit scholarships
- **viewer**: Read-only access to scholarships

## 🛡️ Security Features

- JWT-based authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS protection
- Security headers with Helmet
- Password hashing with bcrypt
- Role-based authorization

## 📈 Monitoring

- Request logging with Morgan
- Error handling and logging
- Audit trail for all operations
- Health check endpoint at `/health`

## 🚀 Deployment

The backend can be deployed to any Node.js hosting platform:

- Heroku, Railway, Render, or Vercel
- Docker containers
- Traditional VPS servers

Make sure to:
1. Set all environment variables
2. Configure Google Sheets access
3. Set up proper HTTPS in production
4. Configure CORS for your domain

## 🧪 Testing

```bash
# Run tests (when implemented)
npm test

# Lint code
npm run lint
```

## 📝 API Response Format

All API responses follow this format:

```json
{
  "success": true|false,
  "data": {}, // Response data
  "message": "Human readable message",
  "errors": [], // Validation errors (if any)
  "pagination": {} // For paginated responses
}
```

## 🔄 Development Workflow

1. Make changes to TypeScript files in `src/`
2. The development server will automatically restart
3. Test your changes using the API endpoints
4. Build for production with `npm run build`

## 🆘 Troubleshooting

**Google Sheets API Issues:**
- Verify service account credentials
- Check if sheets are shared with service account
- Ensure Sheets API is enabled in Google Cloud Console

**Authentication Issues:**
- Check JWT_SECRET is set and consistent
- Verify user exists in the system
- Check token expiration

**Rate Limiting:**
- Adjust rate limits in environment variables
- Check if IP is being blocked
