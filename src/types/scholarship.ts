// Core scholarship data interface
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
}

// Search and filter interfaces
export interface SearchFilters {
  searchTerm: string;
  category: string;
  location: string;
  minAmount: number;
  maxAmount: number;
  deadlineFrom: Date | null;
  deadlineTo: Date | null;
  eligibility: string[];
}

export interface SearchResult {
  scholarships: Scholarship[];
  totalCount: number;
  hasMore: boolean;
}

// UI state interfaces
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalPages: number;
}
