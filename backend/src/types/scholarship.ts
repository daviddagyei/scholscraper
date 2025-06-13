// Core scholarship data interface (shared with frontend)
export interface Scholarship {
  id: string;
  title: string;
  description: string;
  amount: string;
  deadline: Date;
  eligibility: string[];
  requirements: string[];
  applicationUrl: string;
  provider: string;
  location: string;
  category: string;
  isActive: boolean;
  // Admin-specific fields
  createdDate?: Date;
  modifiedDate?: Date;
  createdBy?: string;
  lastModifiedBy?: string;
  status?: 'draft' | 'active' | 'inactive' | 'expired';
}

// Raw CSV data interface (before processing)
export interface RawScholarshipData {
  Title: string;
  Description: string;
  Amount: string;
  Deadline: string;
  Eligibility: string;
  Requirements: string;
  'Application URL': string;
  Provider: string;
  Location: string;
  Category: string;
  Status: string;
  'Created Date'?: string;
  'Modified Date'?: string;
  'Created By'?: string;
  'Last Modified By'?: string;
}

// User and Authentication interfaces
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  isActive: boolean;
  createdDate: Date;
  lastLogin?: Date;
}

export type UserRole = 'super_admin' | 'admin' | 'editor' | 'viewer';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
  role: UserRole;
}

// Audit and logging interfaces
export interface AuditAction {
  timestamp: Date;
  action: 'created' | 'updated' | 'deleted' | 'status_changed' | 'login' | 'logout' | 
          'agent_discovery' | 'data_quality_issue' | 'agent_started' | 'agent_completed' | 
          'agent_failed' | 'batch_import' | 'duplicate_detected' | 'agent_error' | 'agent_log';
  scholarshipId?: string;
  userEmail: string;
  changesMade?: string;
  previousValues?: Partial<Scholarship>;
  ipAddress?: string;
}

// Analytics interfaces
export interface AnalyticsData {
  totalScholarships: number;
  activeScholarships: number;
  draftScholarships: number;
  expiredScholarships: number;
  categoryCounts: Record<string, number>;
  recentActivity: AuditAction[];
  monthlyTrends: {
    month: string;
    created: number;
    updated: number;
  }[];
}

// API Response interfaces
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Request interfaces
export interface CreateScholarshipRequest {
  title: string;
  description: string;
  amount: string;
  deadline: string;
  eligibility: string[];
  requirements: string[];
  applicationUrl: string;
  provider: string;
  category: string;
  status?: 'draft' | 'active' | 'inactive';
}

export interface UpdateScholarshipRequest extends Partial<CreateScholarshipRequest> {
  id: string;
}

export interface ScholarshipFilters {
  status?: string;
  category?: string;
  provider?: string;
  createdBy?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

// Error interfaces
export interface ValidationError {
  field: string;
  message: string;
}

export interface AppError extends Error {
  statusCode: number;
  isOperational: boolean;
}

// Google Sheets specific interfaces
export interface SheetRow {
  values: string[];
}

export interface SheetRange {
  range: string;
  values: string[][];
}
