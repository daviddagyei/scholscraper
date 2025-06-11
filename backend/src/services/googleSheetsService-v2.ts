import { google, sheets_v4 } from 'googleapis';
import { 
  Scholarship, 
  RawScholarshipData, 
  AuditAction, 
  SheetRow 
} from '../types/scholarship';

/**
 * Service for managing Google Sheets operations
 */
export class GoogleSheetsService {
  private sheets: sheets_v4.Sheets | null = null;
  private spreadsheetId: string;
  private initialized = false;

  constructor() {
    this.spreadsheetId = process.env.GOOGLE_SHEETS_ID || '';
  }

  /**
   * Initialize Google Sheets authentication
   */
  private async initialize(): Promise<void> {
    if (this.initialized && this.sheets) {
      return;
    }

    if (!this.spreadsheetId) {
      throw new Error('GOOGLE_SHEETS_ID environment variable is required');
    }

    if (!process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY) {
      throw new Error('Google service account credentials are required');
    }

    try {
      // Initialize Google Sheets API
      const auth = new google.auth.GoogleAuth({
        credentials: {
          client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
          private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
        },
        scopes: ['https://www.googleapis.com/auth/spreadsheets'],
      });

      this.sheets = google.sheets({ version: 'v4', auth });
      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize Google Sheets auth:', error);
      throw new Error('Failed to initialize Google Sheets authentication');
    }
  }

  /**
   * Get all scholarships from the main sheet
   */
  async getScholarships(): Promise<Scholarship[]> {
    await this.initialize();
    
    try {
      const response = await this.sheets!.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Scholarships!A2:O', // Skip header row
      });

      const rows = response.data.values || [];
      return rows.map((row, index) => this.transformRowToScholarship(row, index + 2));
    } catch (error) {
      console.error('Error fetching scholarships from Google Sheets:', error);
      // Return empty array instead of throwing for graceful fallback
      return [];
    }
  }

  /**
   * Create a new scholarship
   */
  async createScholarship(scholarship: Omit<Scholarship, 'id'>, userEmail: string): Promise<string> {
    await this.initialize();
    
    try {
      const newRow = this.transformScholarshipToRow(scholarship, userEmail);
      
      const response = await this.sheets!.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Scholarships!A:O',
        valueInputOption: 'RAW',
        requestBody: {
          values: [newRow],
        },
      });

      // Generate ID based on the row number
      const updatedRange = response.data.updates?.updatedRange;
      const rowNumber = updatedRange ? parseInt(updatedRange.split('!A')[1].split(':')[0]) : 0;
      const scholarshipId = `scholarship-${rowNumber}`;

      // Update the ID in the sheet
      await this.sheets!.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range: `Scholarships!A${rowNumber}`,
        valueInputOption: 'RAW',
        requestBody: {
          values: [[scholarshipId]],
        },
      });

      // Log the action
      await this.logAction({
        timestamp: new Date(),
        action: 'created',
        scholarshipId,
        userEmail,
        changesMade: `Created scholarship: ${scholarship.title}`,
      });

      return scholarshipId;
    } catch (error) {
      console.error('Error creating scholarship:', error);
      throw new Error('Failed to create scholarship');
    }
  }

  /**
   * Update an existing scholarship
   */
  async updateScholarship(
    id: string, 
    updates: Partial<Scholarship>, 
    userEmail: string
  ): Promise<void> {
    await this.initialize();
    
    try {
      // First, find the row with this ID
      const rowNumber = await this.findScholarshipRow(id);
      if (!rowNumber) {
        throw new Error('Scholarship not found');
      }

      // Get current scholarship data for audit trail
      const currentResponse = await this.sheets!.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: `Scholarships!A${rowNumber}:O${rowNumber}`,
      });

      const currentRow = currentResponse.data.values?.[0];
      if (!currentRow) {
        throw new Error('Current scholarship data not found');
      }

      const currentScholarship = this.transformRowToScholarship(currentRow, rowNumber);

      // Merge updates with current data
      const updatedScholarship: Scholarship = {
        ...currentScholarship,
        ...updates,
        modifiedDate: new Date(),
        lastModifiedBy: userEmail,
      };

      // Transform to row format
      const updatedRow = this.transformScholarshipToRow(updatedScholarship, userEmail, true);

      // Update the row
      await this.sheets!.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range: `Scholarships!A${rowNumber}:O${rowNumber}`,
        valueInputOption: 'RAW',
        requestBody: {
          values: [updatedRow],
        },
      });

      // Log the action
      await this.logAction({
        timestamp: new Date(),
        action: 'updated',
        scholarshipId: id,
        userEmail,
        changesMade: `Updated fields: ${Object.keys(updates).join(', ')}`,
        previousValues: currentScholarship,
      });
    } catch (error) {
      console.error('Error updating scholarship:', error);
      throw new Error('Failed to update scholarship');
    }
  }

  /**
   * Delete (soft delete) a scholarship
   */
  async deleteScholarship(id: string, userEmail: string): Promise<void> {
    try {
      await this.updateScholarship(id, { 
        isActive: false, 
        status: 'inactive' 
      }, userEmail);

      await this.logAction({
        timestamp: new Date(),
        action: 'deleted',
        scholarshipId: id,
        userEmail,
        changesMade: 'Soft deleted scholarship',
      });
    } catch (error) {
      console.error('Error deleting scholarship:', error);
      throw new Error('Failed to delete scholarship');
    }
  }

  /**
   * Log an action to the audit sheet
   */
  async logAction(action: AuditAction): Promise<void> {
    try {
      await this.initialize();
      
      const auditRow = [
        action.timestamp.toISOString(),
        action.action,
        action.scholarshipId || '',
        action.userEmail,
        action.changesMade || '',
        action.previousValues ? JSON.stringify(action.previousValues) : '',
        action.ipAddress || '',
      ];

      await this.sheets!.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'AuditLog!A:G',
        valueInputOption: 'RAW',
        requestBody: {
          values: [auditRow],
        },
      });
    } catch (error) {
      console.error('Error logging action:', error);
      // Don't throw error for audit logging failures
    }
  }

  /**
   * Get categories from the Categories sheet
   */
  async getCategories(): Promise<string[]> {
    try {
      await this.initialize();
      
      const response = await this.sheets!.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Categories!A2:A', // Skip header row
      });

      return response.data.values?.map(row => row[0]).filter(Boolean) || [];
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Return default categories if sheet doesn't exist
      return [
        'Academic Merit',
        'Community Service',
        'Entrepreneurship',
        'Diversity & Inclusion',
        'Environmental',
        'Need-Based',
        'STEM',
        'Arts & Humanities',
        'Athletics',
        'General'
      ];
    }
  }

  /**
   * Initialize the Google Sheets with proper headers
   */
  async initializeSheets(): Promise<void> {
    await this.initialize();
    
    try {
      // Check if sheets exist, create if they don't
      await this.ensureSheetExists('Scholarships', [
        'ID', 'Title', 'Description', 'Amount', 'Deadline', 'Eligibility', 
        'Requirements', 'Application URL', 'Provider', 'Category', 'Status',
        'Created Date', 'Modified Date', 'Created By', 'Last Modified By'
      ]);

      await this.ensureSheetExists('AuditLog', [
        'Timestamp', 'Action', 'Scholarship ID', 'User Email', 
        'Changes Made', 'Previous Values', 'IP Address'
      ]);

      await this.ensureSheetExists('Categories', [
        'Category Name', 'Description', 'Color Code', 'Active Status'
      ]);
    } catch (error) {
      console.error('Error initializing sheets:', error);
      throw new Error('Failed to initialize Google Sheets');
    }
  }

  /**
   * Test the connection to Google Sheets
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.initialize();
      
      // Try a simple operation to test the connection
      await this.sheets!.spreadsheets.get({
        spreadsheetId: this.spreadsheetId,
      });
      
      return true;
    } catch (error) {
      console.error('Google Sheets connection test failed:', error);
      return false;
    }
  }

  /**
   * Helper method to ensure a sheet exists with proper headers
   */
  private async ensureSheetExists(sheetName: string, headers: string[]): Promise<void> {
    try {
      // Try to get the sheet
      await this.sheets!.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!A1:${String.fromCharCode(64 + headers.length)}1`,
      });
    } catch (error) {
      // Sheet doesn't exist or is empty, create headers
      try {
        await this.sheets!.spreadsheets.values.update({
          spreadsheetId: this.spreadsheetId,
          range: `${sheetName}!A1`,
          valueInputOption: 'RAW',
          requestBody: {
            values: [headers],
          },
        });
      } catch (createError) {
        console.error(`Error creating ${sheetName} sheet:`, createError);
      }
    }
  }

  /**
   * Find the row number for a scholarship by ID
   */
  private async findScholarshipRow(id: string): Promise<number | null> {
    try {
      const response = await this.sheets!.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Scholarships!A:A',
      });

      const rows = response.data.values || [];
      const rowIndex = rows.findIndex(row => row[0] === id);
      return rowIndex >= 0 ? rowIndex + 1 : null;
    } catch (error) {
      console.error('Error finding scholarship row:', error);
      return null;
    }
  }

  /**
   * Transform Google Sheets row to Scholarship object
   */
  private transformRowToScholarship(row: string[], rowNumber: number): Scholarship {
    return {
      id: row[0] || `scholarship-${rowNumber}`,
      title: row[1] || '',
      description: row[2] || '',
      amount: row[3] || '',
      deadline: new Date(row[4] || ''),
      eligibility: row[5] ? row[5].split(',').map(s => s.trim()) : [],
      requirements: row[6] ? row[6].split(',').map(s => s.trim()) : [],
      applicationUrl: row[7] || '',
      provider: row[8] || '',
      location: 'United States', // Fixed for US scholarships
      category: row[9] || 'General',
      isActive: row[10]?.toLowerCase() !== 'inactive',
      status: (row[10]?.toLowerCase() as any) || 'active',
      createdDate: row[11] ? new Date(row[11]) : undefined,
      modifiedDate: row[12] ? new Date(row[12]) : undefined,
      createdBy: row[13] || '',
      lastModifiedBy: row[14] || '',
    };
  }

  /**
   * Transform Scholarship object to Google Sheets row
   */
  private transformScholarshipToRow(
    scholarship: Scholarship | Omit<Scholarship, 'id'>, 
    userEmail: string,
    isUpdate: boolean = false
  ): string[] {
    const now = new Date().toISOString();
    
    return [
      'id' in scholarship ? scholarship.id : '', // ID will be set after creation
      scholarship.title,
      scholarship.description,
      scholarship.amount,
      scholarship.deadline.toISOString().split('T')[0], // Date only
      scholarship.eligibility.join(', '),
      scholarship.requirements.join(', '),
      scholarship.applicationUrl,
      scholarship.provider,
      scholarship.category,
      scholarship.status || (scholarship.isActive ? 'active' : 'inactive'),
      isUpdate ? (scholarship.createdDate?.toISOString() || now) : now, // Created Date
      now, // Modified Date
      isUpdate ? (scholarship.createdBy || userEmail) : userEmail, // Created By
      userEmail, // Last Modified By
    ];
  }
}

// Create instance but don't export singleton to avoid initialization issues
export const createGoogleSheetsService = () => new GoogleSheetsService();

// Export a default instance for backward compatibility, but it won't auto-initialize
export const googleSheetsService = new GoogleSheetsService();
