import { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { 
  User, 
  LoginRequest, 
  CreateUserRequest, 
  AuthTokens,
  ApiResponse 
} from '../types/scholarship';

// Simple in-memory user store for demo - replace with proper database
const users: User[] = [
  {
    id: 'user-1',
    email: process.env.DEFAULT_ADMIN_EMAIL || 'admin@example.com',
    name: 'Default Admin',
    role: 'super_admin',
    isActive: true,
    createdDate: new Date(),
    lastLogin: undefined,
  }
];

// Store hashed passwords separately (in production, this would be in database)
const userPasswords: Record<string, string> = {};

// Initialize default admin password
if (process.env.DEFAULT_ADMIN_PASSWORD) {
  const defaultAdminEmail = process.env.DEFAULT_ADMIN_EMAIL || 'admin@example.com';
  bcrypt.hash(process.env.DEFAULT_ADMIN_PASSWORD, 10).then(hashedPassword => {
    userPasswords[defaultAdminEmail] = hashedPassword;
  });
}

/**
 * Generate JWT tokens for user
 */
const generateTokens = (user: User): AuthTokens => {
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    throw new Error('JWT_SECRET environment variable is required');
  }

  const accessToken = jwt.sign(
    { user: { ...user } },
    jwtSecret,
    { expiresIn: process.env.JWT_EXPIRES_IN || '24h' } as jwt.SignOptions
  );

  const refreshToken = jwt.sign(
    { userId: user.id },
    jwtSecret,
    { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' } as jwt.SignOptions
  );

  return { accessToken, refreshToken };
};

/**
 * User login
 */
export const login = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password }: LoginRequest = req.body;

    // Find user by email
    const user = users.find(u => u.email === email && u.isActive);
    if (!user) {
      res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
      return;
    }

    // Check password
    const hashedPassword = userPasswords[email];
    if (!hashedPassword || !await bcrypt.compare(password, hashedPassword)) {
      res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
      return;
    }

    // Update last login
    user.lastLogin = new Date();

    // Generate tokens
    const tokens = generateTokens(user);

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
        },
        tokens
      },
      message: 'Login successful'
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Refresh access token
 */
export const refreshToken = async (req: Request, res: Response): Promise<void> => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      res.status(401).json({
        success: false,
        message: 'Refresh token required'
      });
      return;
    }

    // Verify refresh token
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      res.status(500).json({
        success: false,
        message: 'Server configuration error'
      });
      return;
    }

    const decoded = jwt.verify(refreshToken, jwtSecret) as any;
    const user = users.find(u => u.id === decoded.userId && u.isActive);

    if (!user) {
      res.status(401).json({
        success: false,
        message: 'Invalid refresh token'
      });
      return;
    }

    // Generate new tokens
    const tokens = generateTokens(user);

    res.json({
      success: true,
      data: { tokens },
      message: 'Token refreshed successfully'
    });
  } catch (error) {
    res.status(401).json({
      success: false,
      message: 'Invalid refresh token'
    });
  }
};

/**
 * Get current user profile
 */
export const getProfile = async (req: Request, res: Response): Promise<void> => {
  try {
    if (!req.user) {
      res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
      return;
    }

    res.json({
      success: true,
      data: {
        id: req.user.id,
        email: req.user.email,
        name: req.user.name,
        role: req.user.role,
        lastLogin: req.user.lastLogin,
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Create new user (super_admin only)
 */
export const createUser = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, name, password, role }: CreateUserRequest = req.body;

    // Check if user already exists
    if (users.find(u => u.email === email)) {
      res.status(400).json({
        success: false,
        message: 'User with this email already exists'
      });
      return;
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const newUser: User = {
      id: `user-${Date.now()}`,
      email,
      name,
      role,
      isActive: true,
      createdDate: new Date(),
    };

    users.push(newUser);
    userPasswords[email] = hashedPassword;

    res.status(201).json({
      success: true,
      data: {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name,
        role: newUser.role,
        createdDate: newUser.createdDate,
      },
      message: 'User created successfully'
    });
  } catch (error) {
    console.error('Create user error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Get all users (admin+ only)
 */
export const getUsers = async (req: Request, res: Response): Promise<void> => {
  try {
    const activeUsers = users
      .filter(u => u.isActive)
      .map(u => ({
        id: u.id,
        email: u.email,
        name: u.name,
        role: u.role,
        createdDate: u.createdDate,
        lastLogin: u.lastLogin,
      }));

    res.json({
      success: true,
      data: activeUsers
    });
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Update user (admin+ only)
 */
export const updateUser = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { name, role, isActive } = req.body;

    const user = users.find(u => u.id === id);
    if (!user) {
      res.status(404).json({
        success: false,
        message: 'User not found'
      });
      return;
    }

    // Update user fields
    if (name !== undefined) user.name = name;
    if (role !== undefined) user.role = role;
    if (isActive !== undefined) user.isActive = isActive;

    res.json({
      success: true,
      data: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        isActive: user.isActive,
      },
      message: 'User updated successfully'
    });
  } catch (error) {
    console.error('Update user error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Logout (optional - mainly for audit purposes)
 */
export const logout = async (req: Request, res: Response): Promise<void> => {
  try {
    // In a real implementation, you might want to blacklist the token
    // or store active sessions in a database
    
    res.json({
      success: true,
      message: 'Logout successful'
    });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};
