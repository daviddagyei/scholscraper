import { Scholarship } from '../types/scholarship';

/**
 * Utility functions for data validation
 */

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate URL format
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate date is in the future
 */
export const isFutureDate = (date: Date): boolean => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date > today;
};

/**
 * Sanitize string input
 */
export const sanitizeString = (input: string): string => {
  return input.trim().replace(/[<>]/g, '');
};

/**
 * Validate scholarship data
 */
export const validateScholarshipData = (scholarship: Partial<Scholarship>): string[] => {
  const errors: string[] = [];

  if (!scholarship.title || scholarship.title.trim().length === 0) {
    errors.push('Title is required');
  } else if (scholarship.title.length > 200) {
    errors.push('Title must be less than 200 characters');
  }

  if (!scholarship.description || scholarship.description.trim().length === 0) {
    errors.push('Description is required');
  } else if (scholarship.description.length > 2000) {
    errors.push('Description must be less than 2000 characters');
  }

  if (!scholarship.amount || scholarship.amount.trim().length === 0) {
    errors.push('Amount is required');
  }

  if (!scholarship.deadline) {
    errors.push('Deadline is required');
  } else if (!isFutureDate(scholarship.deadline)) {
    errors.push('Deadline must be in the future');
  }

  if (!scholarship.eligibility || scholarship.eligibility.length === 0) {
    errors.push('At least one eligibility criterion is required');
  }

  if (!scholarship.requirements || scholarship.requirements.length === 0) {
    errors.push('At least one requirement is required');
  }

  if (!scholarship.applicationUrl || !isValidUrl(scholarship.applicationUrl)) {
    errors.push('Valid application URL is required');
  }

  if (!scholarship.provider || scholarship.provider.trim().length === 0) {
    errors.push('Provider is required');
  }

  if (!scholarship.category || scholarship.category.trim().length === 0) {
    errors.push('Category is required');
  }

  return errors;
};

/**
 * Generate a unique ID
 */
export const generateId = (prefix: string = 'id'): string => {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return `${prefix}-${timestamp}-${random}`;
};

/**
 * Parse amount string and extract numeric value
 */
export const parseAmount = (amount: string): number | null => {
  const cleanAmount = amount.replace(/[^0-9.,]/g, '');
  const numericValue = parseFloat(cleanAmount.replace(/,/g, ''));
  return isNaN(numericValue) ? null : numericValue;
};

/**
 * Format amount for display
 */
export const formatAmount = (amount: string): string => {
  const numericValue = parseAmount(amount);
  if (numericValue === null) return amount;
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numericValue);
};

/**
 * Check if a string contains potentially harmful content
 */
export const containsHarmfulContent = (input: string): boolean => {
  const harmfulPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
  ];
  
  return harmfulPatterns.some(pattern => pattern.test(input));
};

/**
 * Deep sanitize an object
 */
export const sanitizeObject = (obj: any): any => {
  if (typeof obj === 'string') {
    return sanitizeString(obj);
  }
  
  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject);
  }
  
  if (obj && typeof obj === 'object') {
    const sanitized: any = {};
    for (const [key, value] of Object.entries(obj)) {
      sanitized[key] = sanitizeObject(value);
    }
    return sanitized;
  }
  
  return obj;
};
