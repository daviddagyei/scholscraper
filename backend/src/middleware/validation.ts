import { Request, Response, NextFunction } from 'express';
import { body, validationResult, ValidationChain } from 'express-validator';

/**
 * Middleware to handle validation errors
 */
export const handleValidationErrors = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    res.status(400).json({
      success: false,
      message: 'Validation errors',
      errors: errors.array().map(error => ({
        field: error.type === 'field' ? (error as any).path : 'unknown',
        message: error.msg
      }))
    });
    return;
  }
  
  next();
};

/**
 * Validation rules for creating/updating scholarships
 */
export const validateScholarship: ValidationChain[] = [
  body('title')
    .trim()
    .isLength({ min: 1, max: 200 })
    .withMessage('Title must be between 1 and 200 characters'),
  
  body('description')
    .trim()
    .isLength({ min: 1, max: 2000 })
    .withMessage('Description must be between 1 and 2000 characters'),
  
  body('amount')
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Amount is required and must be less than 50 characters'),
  
  body('deadline')
    .isISO8601()
    .withMessage('Deadline must be a valid date in ISO 8601 format')
    .custom((value) => {
      const deadline = new Date(value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (deadline < today) {
        throw new Error('Deadline cannot be in the past');
      }
      return true;
    }),
  
  body('eligibility')
    .isArray({ min: 1 })
    .withMessage('At least one eligibility criterion is required')
    .custom((value: string[]) => {
      if (!value.every(item => typeof item === 'string' && item.trim().length > 0)) {
        throw new Error('All eligibility criteria must be non-empty strings');
      }
      return true;
    }),
  
  body('requirements')
    .isArray({ min: 1 })
    .withMessage('At least one requirement is required')
    .custom((value: string[]) => {
      if (!value.every(item => typeof item === 'string' && item.trim().length > 0)) {
        throw new Error('All requirements must be non-empty strings');
      }
      return true;
    }),
  
  body('applicationUrl')
    .trim()
    .isURL()
    .withMessage('Application URL must be a valid URL'),
  
  body('provider')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Provider must be between 1 and 100 characters'),
  
  body('category')
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Category must be between 1 and 50 characters'),
  
  body('status')
    .optional()
    .isIn(['draft', 'active', 'inactive'])
    .withMessage('Status must be one of: draft, active, inactive')
];

/**
 * Validation rules for user authentication
 */
export const validateLogin: ValidationChain[] = [
  body('email')
    .trim()
    .isEmail()
    .normalizeEmail()
    .withMessage('Valid email is required'),
  
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
];

/**
 * Validation rules for creating users
 */
export const validateCreateUser: ValidationChain[] = [
  body('email')
    .trim()
    .isEmail()
    .normalizeEmail()
    .withMessage('Valid email is required'),
  
  body('name')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Name must be between 1 and 100 characters'),
  
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one lowercase letter, one uppercase letter, and one number'),
  
  body('role')
    .isIn(['super_admin', 'admin', 'editor', 'viewer'])
    .withMessage('Role must be one of: super_admin, admin, editor, viewer')
];

/**
 * Validation rules for updating scholarships (partial)
 */
export const validateUpdateScholarship: ValidationChain[] = [
  body('title')
    .optional()
    .trim()
    .isLength({ min: 1, max: 200 })
    .withMessage('Title must be between 1 and 200 characters'),
  
  body('description')
    .optional()
    .trim()
    .isLength({ min: 1, max: 2000 })
    .withMessage('Description must be between 1 and 2000 characters'),
  
  body('amount')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Amount must be less than 50 characters'),
  
  body('deadline')
    .optional()
    .isISO8601()
    .withMessage('Deadline must be a valid date in ISO 8601 format'),
  
  body('eligibility')
    .optional()
    .isArray({ min: 1 })
    .withMessage('Eligibility must be an array with at least one item'),
  
  body('requirements')
    .optional()
    .isArray({ min: 1 })
    .withMessage('Requirements must be an array with at least one item'),
  
  body('applicationUrl')
    .optional()
    .trim()
    .isURL()
    .withMessage('Application URL must be a valid URL'),
  
  body('provider')
    .optional()
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Provider must be between 1 and 100 characters'),
  
  body('category')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Category must be between 1 and 50 characters'),
  
  body('status')
    .optional()
    .isIn(['draft', 'active', 'inactive'])
    .withMessage('Status must be one of: draft, active, inactive')
];
