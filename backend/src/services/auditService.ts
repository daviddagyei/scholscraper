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
   * Log scholarship discovery agent activity
   */
  async logAgentActivity(result: {
    success: boolean;
    scholarships_discovered?: number;
    scholarships_saved?: number;
    scholarships_skipped?: number;
    search_criteria?: string;
    timestamp?: string;
    duration_seconds?: number;
    pipeline_type?: string;
    error?: string;
  }): Promise<void> {
    try {
      const action: AuditAction = {
        timestamp: new Date(result.timestamp || Date.now()),
        action: 'agent_discovery',
        scholarshipId: 'system',
        userEmail: 'scholarship-agent@system',
        changesMade: this.formatAgentActivityLog(result)
      };

      await this.logAction(action);
    } catch (error) {
      console.error('Error logging agent activity:', error);
    }
  }

  /**
   * Format agent activity for audit log
   */
  private formatAgentActivityLog(result: any): string {
    if (!result.success) {
      return `Agent discovery failed: ${result.error || 'Unknown error'}`;
    }

    const parts = [
      `Discovery completed with ${result.pipeline_type || 'standard pipeline'}`,
      `Criteria: "${result.search_criteria || 'Default'}"`,
      `Found: ${result.scholarships_discovered || 0} scholarships`,
      `Saved: ${result.scholarships_saved || 0} scholarships`,
      `Skipped: ${result.scholarships_skipped || 0} scholarships`,
      `Duration: ${(result.duration_seconds || 0).toFixed(1)}s`
    ];

    if (result.save_error) {
      parts.push(`Save warning: ${result.save_error}`);
    }

    return parts.join(' | ');
  }

  /**
   * Get agent activity statistics
   */
  async getAgentStatistics(days: number = 30): Promise<{
    total_runs: number;
    successful_runs: number;
    total_scholarships_discovered: number;
    total_scholarships_saved: number;
    average_duration: number;
    recent_activities: any[];
  }> {
    try {
      // This would ideally query an audit log database or sheet
      // For now, we'll return basic statistics structure
      return {
        total_runs: 0,
        successful_runs: 0,
        total_scholarships_discovered: 0,
        total_scholarships_saved: 0,
        average_duration: 0,
        recent_activities: []
      };
    } catch (error) {
      console.error('Error getting agent statistics:', error);
      throw error;
    }
  }

  /**
   * Log data quality issues found during agent runs
   */
  async logDataQualityIssues(issues: {
    scholarshipTitle: string;
    issueType: 'missing_field' | 'invalid_format' | 'duplicate' | 'low_quality';
    description: string;
    severity: 'low' | 'medium' | 'high';
  }[]): Promise<void> {
    try {
      for (const issue of issues) {
        const action: AuditAction = {
          timestamp: new Date(),
          action: 'data_quality_issue',
          scholarshipId: issue.scholarshipTitle,
          userEmail: 'scholarship-agent@system',
          changesMade: `${issue.issueType}: ${issue.description} (Severity: ${issue.severity})`
        };

        await this.logAction(action);
      }
    } catch (error) {
      console.error('Error logging data quality issues:', error);
    }
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

  /**
   * Log the start of an agent discovery session
   */
  async logAgentStart(searchCriteria: string): Promise<void> {
    try {
      const action: AuditAction = {
        timestamp: new Date(),
        action: 'agent_started',
        scholarshipId: 'system',
        userEmail: 'scholarship-agent@system',
        changesMade: `Agent discovery started with criteria: "${searchCriteria}"`
      };

      await this.logAction(action);
    } catch (error) {
      console.error('Error logging agent start:', error);
    }
  }

  /**
   * Log agent completion with detailed results
   */
  async logAgentCompletion(result: {
    success: boolean;
    scholarships_discovered?: number;
    scholarships_saved?: number;
    scholarships_skipped?: number;
    duration_seconds?: number;
    error?: string;
  }): Promise<void> {
    try {
      const action: AuditAction = {
        timestamp: new Date(),
        action: result.success ? 'agent_completed' : 'agent_failed',
        scholarshipId: 'system',
        userEmail: 'scholarship-agent@system',
        changesMade: result.success 
          ? `Agent completed successfully: ${result.scholarships_discovered || 0} discovered, ${result.scholarships_saved || 0} saved, ${result.scholarships_skipped || 0} skipped in ${(result.duration_seconds || 0).toFixed(1)}s`
          : `Agent failed: ${result.error || 'Unknown error'}`
      };

      await this.logAction(action);
    } catch (error) {
      console.error('Error logging agent completion:', error);
    }
  }

  /**
   * Log batch import activities
   */
  async logBatchImport(scholarshipIds: string[], userEmail: string = 'scholarship-agent@system'): Promise<void> {
    try {
      const action: AuditAction = {
        timestamp: new Date(),
        action: 'batch_import',
        scholarshipId: 'batch',
        userEmail,
        changesMade: `Batch import of ${scholarshipIds.length} scholarships: ${scholarshipIds.slice(0, 3).join(', ')}${scholarshipIds.length > 3 ? '...' : ''}`
      };

      await this.logAction(action);
    } catch (error) {
      console.error('Error logging batch import:', error);
    }
  }

  /**
   * Log duplicate detection
   */
  async logDuplicateDetected(scholarshipTitle: string, existingId?: string): Promise<void> {
    try {
      const action: AuditAction = {
        timestamp: new Date(),
        action: 'duplicate_detected',
        scholarshipId: existingId || 'unknown',
        userEmail: 'scholarship-agent@system',
        changesMade: `Duplicate scholarship detected and skipped: "${scholarshipTitle}"`
      };

      await this.logAction(action);
    } catch (error) {
      console.error('Error logging duplicate detection:', error);
    }
  }
}

// Export singleton instance
export const auditService = new AuditService();
export { AuditService };
