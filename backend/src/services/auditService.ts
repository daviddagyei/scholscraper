import { AuditAction } from '../types/scholarship';
import { googleSheetsService } from './googleSheetsService';

/**
 * Service for handling audit logging and activity tracking
 */
class AuditService {
  private auditQueue: AuditAction[] = [];
  private isProcessing = false;

  /**
   * Log an action
   */
  async logAction(action: AuditAction): Promise<void> {
    try {
      // Add to queue for batch processing
      this.auditQueue.push(action);
      
      // Process queue if not already processing
      if (!this.isProcessing) {
        this.processQueue();
      }
    } catch (error) {
      console.error('Error queuing audit action:', error);
    }
  }

  /**
   * Process the audit queue
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.auditQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    try {
      while (this.auditQueue.length > 0) {
        const action = this.auditQueue.shift();
        if (action) {
          await googleSheetsService.logAction(action);
        }
      }
    } catch (error) {
      console.error('Error processing audit queue:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Get recent audit actions (this would typically come from the audit sheet)
   */
  async getRecentActions(limit: number = 10): Promise<AuditAction[]> {
    // In a full implementation, this would fetch from the AuditLog sheet
    // For now, return empty array as the data would come from Google Sheets
    return [];
  }

  /**
   * Log user login
   */
  async logLogin(userEmail: string, ipAddress?: string): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'login',
      userEmail,
      changesMade: 'User logged in',
      ipAddress,
    });
  }

  /**
   * Log user logout
   */
  async logLogout(userEmail: string, ipAddress?: string): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'logout',
      userEmail,
      changesMade: 'User logged out',
      ipAddress,
    });
  }

  /**
   * Log scholarship creation
   */
  async logScholarshipCreated(
    scholarshipId: string,
    userEmail: string,
    scholarshipTitle: string,
    ipAddress?: string
  ): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'created',
      scholarshipId,
      userEmail,
      changesMade: `Created scholarship: ${scholarshipTitle}`,
      ipAddress,
    });
  }

  /**
   * Log scholarship update
   */
  async logScholarshipUpdated(
    scholarshipId: string,
    userEmail: string,
    changedFields: string[],
    previousValues?: any,
    ipAddress?: string
  ): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'updated',
      scholarshipId,
      userEmail,
      changesMade: `Updated fields: ${changedFields.join(', ')}`,
      previousValues,
      ipAddress,
    });
  }

  /**
   * Log scholarship deletion
   */
  async logScholarshipDeleted(
    scholarshipId: string,
    userEmail: string,
    scholarshipTitle: string,
    ipAddress?: string
  ): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'deleted',
      scholarshipId,
      userEmail,
      changesMade: `Deleted scholarship: ${scholarshipTitle}`,
      ipAddress,
    });
  }

  /**
   * Log status change
   */
  async logStatusChanged(
    scholarshipId: string,
    userEmail: string,
    oldStatus: string,
    newStatus: string,
    ipAddress?: string
  ): Promise<void> {
    await this.logAction({
      timestamp: new Date(),
      action: 'status_changed',
      scholarshipId,
      userEmail,
      changesMade: `Status changed from ${oldStatus} to ${newStatus}`,
      ipAddress,
    });
  }

  /**
   * Get audit statistics
   */
  async getAuditStatistics(): Promise<{
    totalActions: number;
    actionsByType: Record<string, number>;
    actionsByUser: Record<string, number>;
    recentActivityCount: number;
  }> {
    // In a full implementation, this would analyze the AuditLog sheet
    // For now, return mock data
    return {
      totalActions: 0,
      actionsByType: {},
      actionsByUser: {},
      recentActivityCount: 0,
    };
  }
}

// Export singleton instance
export const auditService = new AuditService();
export { AuditService };
