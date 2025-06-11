import { Request, Response } from 'express';
import { 
  Scholarship, 
  CreateScholarshipRequest, 
  UpdateScholarshipRequest,
  ScholarshipFilters,
  ApiResponse,
  PaginatedResponse,
  AnalyticsData
} from '../types/scholarship';
import { googleSheetsService } from '../services/googleSheetsService';

/**
 * Get all scholarships with filtering and pagination
 */
export const getScholarships = async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      status,
      category,
      provider,
      createdBy,
      dateFrom,
      dateTo,
      search,
      page = '1',
      limit = '20'
    } = req.query as any;

    // Get all scholarships from Google Sheets
    let scholarships = await googleSheetsService.getScholarships();

    // Apply filters
    if (status) {
      scholarships = scholarships.filter((s: Scholarship) => s.status === status);
    }

    if (category) {
      scholarships = scholarships.filter((s: Scholarship) => 
        s.category.toLowerCase().includes(category.toLowerCase())
      );
    }

    if (provider) {
      scholarships = scholarships.filter((s: Scholarship) => 
        s.provider.toLowerCase().includes(provider.toLowerCase())
      );
    }

    if (createdBy) {
      scholarships = scholarships.filter((s: Scholarship) => 
        s.createdBy?.toLowerCase().includes(createdBy.toLowerCase())
      );
    }

    if (dateFrom) {
      const fromDate = new Date(dateFrom);
      scholarships = scholarships.filter((s: Scholarship) => 
        s.createdDate && s.createdDate >= fromDate
      );
    }

    if (dateTo) {
      const toDate = new Date(dateTo);
      scholarships = scholarships.filter((s: Scholarship) => 
        s.createdDate && s.createdDate <= toDate
      );
    }

    if (search) {
      const searchTerm = search.toLowerCase();
      scholarships = scholarships.filter((s: Scholarship) => 
        s.title.toLowerCase().includes(searchTerm) ||
        s.description.toLowerCase().includes(searchTerm) ||
        s.provider.toLowerCase().includes(searchTerm)
      );
    }

    // Sort by created date (newest first)
    scholarships.sort((a: Scholarship, b: Scholarship) => {
      const dateA = a.createdDate || new Date(0);
      const dateB = b.createdDate || new Date(0);
      return dateB.getTime() - dateA.getTime();
    });

    // Pagination
    const pageNum = parseInt(page);
    const limitNum = parseInt(limit);
    const startIndex = (pageNum - 1) * limitNum;
    const endIndex = startIndex + limitNum;
    
    const paginatedScholarships = scholarships.slice(startIndex, endIndex);
    const totalPages = Math.ceil(scholarships.length / limitNum);

    const response: PaginatedResponse<Scholarship> = {
      success: true,
      data: paginatedScholarships,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total: scholarships.length,
        totalPages
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Get scholarships error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch scholarships'
    });
  }
};

/**
 * Get public scholarships (for frontend)
 */
export const getPublicScholarships = async (req: Request, res: Response): Promise<void> => {
  try {
    let scholarships = await googleSheetsService.getScholarships();
    
    // Filter only active scholarships for public API
    scholarships = scholarships.filter((s: Scholarship) => s.isActive && s.status === 'active');
    
    // Remove admin-specific fields
    const publicScholarships = scholarships.map((s: Scholarship) => ({
      id: s.id,
      title: s.title,
      description: s.description,
      amount: s.amount,
      deadline: s.deadline,
      eligibility: s.eligibility,
      requirements: s.requirements,
      applicationUrl: s.applicationUrl,
      provider: s.provider,
      location: s.location,
      category: s.category,
      isActive: s.isActive
    }));

    res.json({
      success: true,
      data: publicScholarships
    });
  } catch (error) {
    console.error('Get public scholarships error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch scholarships'
    });
  }
};

/**
 * Get scholarship by ID
 */
export const getScholarshipById = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const scholarships = await googleSheetsService.getScholarships();
    const scholarship = scholarships.find((s: Scholarship) => s.id === id);

    if (!scholarship) {
      res.status(404).json({
        success: false,
        message: 'Scholarship not found'
      });
      return;
    }

    res.json({
      success: true,
      data: scholarship
    });
  } catch (error) {
    console.error('Get scholarship by ID error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch scholarship'
    });
  }
};

/**
 * Create new scholarship
 */
export const createScholarship = async (req: Request, res: Response): Promise<void> => {
  try {
    const scholarshipData: CreateScholarshipRequest = req.body;
    const userEmail = req.user?.email || 'unknown';

    const newScholarship: Omit<Scholarship, 'id'> = {
      title: scholarshipData.title,
      description: scholarshipData.description,
      amount: scholarshipData.amount,
      deadline: new Date(scholarshipData.deadline),
      eligibility: scholarshipData.eligibility,
      requirements: scholarshipData.requirements,
      applicationUrl: scholarshipData.applicationUrl,
      provider: scholarshipData.provider,
      location: 'United States', // Fixed for US scholarships
      category: scholarshipData.category,
      isActive: scholarshipData.status !== 'inactive',
      status: scholarshipData.status || 'active',
      createdDate: new Date(),
      createdBy: userEmail,
    };

    const scholarshipId = await googleSheetsService.createScholarship(newScholarship, userEmail);

    res.status(201).json({
      success: true,
      data: { id: scholarshipId, ...newScholarship },
      message: 'Scholarship created successfully'
    });
  } catch (error) {
    console.error('Create scholarship error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create scholarship'
    });
  }
};

/**
 * Update scholarship
 */
export const updateScholarship = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updates: Partial<CreateScholarshipRequest> = req.body;
    const userEmail = req.user?.email || 'unknown';

    // Convert updates to proper format
    const scholarshipUpdates: Partial<Scholarship> = {};

    if (updates.title !== undefined) scholarshipUpdates.title = updates.title;
    if (updates.description !== undefined) scholarshipUpdates.description = updates.description;
    if (updates.amount !== undefined) scholarshipUpdates.amount = updates.amount;
    if (updates.deadline !== undefined) scholarshipUpdates.deadline = new Date(updates.deadline);
    if (updates.eligibility !== undefined) scholarshipUpdates.eligibility = updates.eligibility;
    if (updates.requirements !== undefined) scholarshipUpdates.requirements = updates.requirements;
    if (updates.applicationUrl !== undefined) scholarshipUpdates.applicationUrl = updates.applicationUrl;
    if (updates.provider !== undefined) scholarshipUpdates.provider = updates.provider;
    if (updates.category !== undefined) scholarshipUpdates.category = updates.category;
    if (updates.status !== undefined) {
      scholarshipUpdates.status = updates.status;
      scholarshipUpdates.isActive = updates.status !== 'inactive';
    }

    await googleSheetsService.updateScholarship(id, scholarshipUpdates, userEmail);

    res.json({
      success: true,
      message: 'Scholarship updated successfully'
    });
  } catch (error) {
    console.error('Update scholarship error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update scholarship'
    });
  }
};

/**
 * Delete scholarship (soft delete)
 */
export const deleteScholarship = async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const userEmail = req.user?.email || 'unknown';

    await googleSheetsService.deleteScholarship(id, userEmail);

    res.json({
      success: true,
      message: 'Scholarship deleted successfully'
    });
  } catch (error) {
    console.error('Delete scholarship error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete scholarship'
    });
  }
};

/**
 * Get available categories
 */
export const getCategories = async (req: Request, res: Response): Promise<void> => {
  try {
    const categories = await googleSheetsService.getCategories();

    res.json({
      success: true,
      data: categories
    });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch categories'
    });
  }
};

/**
 * Get analytics data
 */
export const getAnalytics = async (req: Request, res: Response): Promise<void> => {
  try {
    const scholarships = await googleSheetsService.getScholarships();
    
    // Calculate analytics
    const totalScholarships = scholarships.length;
    const activeScholarships = scholarships.filter((s: Scholarship) => s.status === 'active').length;
    const draftScholarships = scholarships.filter((s: Scholarship) => s.status === 'draft').length;
    const expiredScholarships = scholarships.filter((s: Scholarship) => s.deadline < new Date()).length;

    // Category counts
    const categoryCounts: Record<string, number> = {};
    scholarships.forEach((s: Scholarship) => {
      categoryCounts[s.category] = (categoryCounts[s.category] || 0) + 1;
    });

    // Monthly trends (last 6 months)
    const monthlyTrends = [];
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const month = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthStr = month.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
      
      const created = scholarships.filter((s: Scholarship) => {
        const createdDate = s.createdDate;
        return createdDate && 
               createdDate.getFullYear() === month.getFullYear() &&
               createdDate.getMonth() === month.getMonth();
      }).length;
      
      const updated = scholarships.filter((s: Scholarship) => {
        const modifiedDate = s.modifiedDate;
        return modifiedDate && 
               modifiedDate.getFullYear() === month.getFullYear() &&
               modifiedDate.getMonth() === month.getMonth() &&
               s.createdDate !== s.modifiedDate; // Only count actual updates
      }).length;

      monthlyTrends.push({
        month: monthStr,
        created,
        updated
      });
    }

    const analytics: AnalyticsData = {
      totalScholarships,
      activeScholarships,
      draftScholarships,
      expiredScholarships,
      categoryCounts,
      recentActivity: [], // Would come from audit log in real implementation
      monthlyTrends
    };

    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Get analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch analytics'
    });
  }
};

/**
 * Bulk update scholarships
 */
export const bulkUpdateScholarships = async (req: Request, res: Response): Promise<void> => {
  try {
    const { scholarshipIds, updates } = req.body;
    const userEmail = req.user?.email || 'unknown';

    if (!Array.isArray(scholarshipIds) || scholarshipIds.length === 0) {
      res.status(400).json({
        success: false,
        message: 'Scholarship IDs array is required'
      });
      return;
    }

    const results = [];
    for (const id of scholarshipIds) {
      try {
        await googleSheetsService.updateScholarship(id, updates, userEmail);
        results.push({ id, success: true });
      } catch (error) {
        results.push({ id, success: false, error: error instanceof Error ? error.message : 'Unknown error' });
      }
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.length - successCount;

    res.json({
      success: true,
      data: {
        results,
        summary: {
          total: results.length,
          successful: successCount,
          failed: failureCount
        }
      },
      message: `Bulk update completed: ${successCount} successful, ${failureCount} failed`
    });
  } catch (error) {
    console.error('Bulk update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to perform bulk update'
    });
  }
};
