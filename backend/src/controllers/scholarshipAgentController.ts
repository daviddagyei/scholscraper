import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { auditService } from '../services/auditService';

interface AgentResult {
  success: boolean;
  scholarships_discovered?: number;
  scholarships_saved?: number;
  scholarships_skipped?: number;
  search_criteria?: string;
  timestamp?: string;
  duration_seconds?: number;
  sources_count?: number;
  pipeline_type?: string;
  save_error?: string;
  sample_scholarships?: any[];
  error?: string;
  output?: string;
  quality_report?: {
    high_quality: number;
    medium_quality: number;
    low_quality: number;
  };
}

export class ScholarshipAgentController {
  private agentPath: string;

  constructor() {
    this.agentPath = path.join(__dirname, '../../langgraph-agent/backend/run_agent.py');
  }

  /**
   * Run the scholarship discovery agent with enhanced JSON-first pipeline
   */
  async runDiscovery(searchCriteria?: string): Promise<AgentResult> {
    const finalSearchCriteria = searchCriteria || "new scholarships for college students 2025";
    
    // Log agent start
    auditService.logAgentStart(finalSearchCriteria).catch(error => 
      console.warn('Failed to log agent start:', error)
    );

    return new Promise((resolve) => {
      const args = ['--daily'];
      if (searchCriteria) {
        args.push('--search', searchCriteria);
      }

      // Add timestamp for output file
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const outputFile = path.join(__dirname, `../../langgraph-agent/backend/logs/discovery_${timestamp}.json`);
      args.push('--output', outputFile);

      console.log(`🚀 Running enhanced scholarship agent with args: ${args.join(' ')}`);
      console.log(`📂 Output file: ${outputFile}`);

      const pythonProcess = spawn('python3', [this.agentPath, ...args], {
        cwd: path.dirname(this.agentPath),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        // Log interesting output in real-time
        if (output.includes('DEBUG:') || output.includes('Scholarships discovered:') || output.includes('ERROR:')) {
          console.log('Agent output:', output.trim());
        }
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error('Agent stderr:', data.toString());
      });

      pythonProcess.on('close', (code) => {
        console.log(`🏁 Scholarship agent process finished with code: ${code}`);
        
        if (code === 0) {
          // Try to read the output file for detailed results
          try {
            if (fs.existsSync(outputFile)) {
              const resultData = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
              
              // Enhanced result with new JSON pipeline data
              const enhancedResult: AgentResult = {
                success: resultData.success || true,
                scholarships_discovered: resultData.scholarships_discovered || 0,
                scholarships_saved: resultData.scholarships_saved || 0,
                scholarships_skipped: resultData.scholarships_skipped || 0,
                search_criteria: resultData.search_criteria,
                timestamp: resultData.timestamp,
                duration_seconds: resultData.duration_seconds,
                sources_count: resultData.sources_count,
                pipeline_type: resultData.pipeline_type || "JSON-first enhanced pipeline",
                save_error: resultData.save_error,
                sample_scholarships: resultData.sample_scholarships,
                output: stdout
              };
              
              // Add quality report if scholarships are present
              if (resultData.scholarships && Array.isArray(resultData.scholarships)) {
                enhancedResult.quality_report = this.generateQualityReport(resultData.scholarships);
              }
              
              console.log(`📊 Discovery completed: ${enhancedResult.scholarships_discovered} found, ${enhancedResult.scholarships_saved} saved`);
              
              // Log agent completion (non-blocking)
              auditService.logAgentCompletion(enhancedResult).catch(auditError => {
                console.warn('Failed to log agent completion:', auditError);
              });
              
              // Log batch import if scholarships were saved
              if (enhancedResult.scholarships_saved && enhancedResult.scholarships_saved > 0 && enhancedResult.sample_scholarships) {
                const scholarshipIds = enhancedResult.sample_scholarships.map(s => s.id || `temp-${Date.now()}`);
                auditService.logBatchImport(scholarshipIds).catch(auditError => {
                  console.warn('Failed to log batch import:', auditError);
                });
              }
              
              resolve(enhancedResult);
            } else {
              console.log('⚠️  No output file found, returning basic success');
              
              // Log completion without detailed results
              auditService.logAgentCompletion({ success: true }).catch(error => 
                console.warn('Failed to log agent completion:', error)
              );
              
              resolve({
                success: true,
                output: stdout
              });
            }
          } catch (error) {
            console.error('❌ Error parsing result file:', error);
            
            // Log agent failure
            auditService.logAgentCompletion({ 
              success: false, 
              error: `Could not parse result file: ${error}` 
            }).catch(auditError => {
              console.warn('Failed to log agent failure:', auditError);
            });
            
            resolve({
              success: true,
              output: stdout,
              error: `Could not parse result file: ${error}`
            });
          }
        } else {
          console.error(`❌ Agent failed with exit code ${code}`);
          
          // Log agent failure
          auditService.logAgentCompletion({ 
            success: false, 
            error: `Agent failed with exit code ${code}. stderr: ${stderr}` 
          }).catch(auditError => {
            console.warn('Failed to log agent failure:', auditError);
          });
          
          resolve({
            success: false,
            error: `Agent failed with exit code ${code}. stderr: ${stderr}`,
            output: stdout
          });
        }
      });

      pythonProcess.on('error', (error) => {
        console.error('💥 Failed to start agent:', error);
        
        // Log agent failure
        auditService.logAgentCompletion({ 
          success: false, 
          error: `Failed to start agent: ${error.message}` 
        }).catch(auditError => {
          console.warn('Failed to log agent failure:', auditError);
        });
        
        resolve({
          success: false,
          error: `Failed to start agent: ${error.message}`
        });
      });
    });
  }

  /**
   * Generate quality report for discovered scholarships
   */
  private generateQualityReport(scholarships: any[]): { high_quality: number; medium_quality: number; low_quality: number } {
    const report = { high_quality: 0, medium_quality: 0, low_quality: 0 };
    
    for (const scholarship of scholarships) {
      const requiredFields = ['title', 'description', 'amount', 'deadline', 'provider', 'applicationUrl'];
      const presentFields = requiredFields.filter(field => 
        scholarship[field] && scholarship[field] !== 'Not available' && scholarship[field].trim() !== ''
      ).length;
      
      if (presentFields >= 5) {
        report.high_quality++;
      } else if (presentFields >= 3) {
        report.medium_quality++;
      } else {
        report.low_quality++;
      }
    }
    
    return report;
  }

  /**
   * Check if the agent is properly configured
   */
  checkConfiguration(): { configured: boolean; issues: string[] } {
    const issues: string[] = [];

    // Check if Python script exists
    if (!fs.existsSync(this.agentPath)) {
      issues.push('Scholarship agent script not found');
    }

    // Check if Gemini API key is configured
    if (!process.env.GEMINI_API_KEY || process.env.GEMINI_API_KEY === 'your_gemini_api_key_here') {
      issues.push('GEMINI_API_KEY not configured');
    }

    // Check if Google Sheets credentials are available
    if (!process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY) {
      issues.push('Google Sheets credentials not configured');
    }

    return {
      configured: issues.length === 0,
      issues
    };
  }

  /**
   * Get agent status and recent runs
   */
  getAgentStatus() {
    const config = this.checkConfiguration();
    const logsDir = path.join(path.dirname(this.agentPath), 'logs');
    
    let recentRuns: string[] = [];
    if (fs.existsSync(logsDir)) {
      recentRuns = fs.readdirSync(logsDir)
        .filter(file => file.startsWith('discovery_') && file.endsWith('.json'))
        .sort()
        .reverse()
        .slice(0, 5);
    }

    return {
      ...config,
      agent_path: this.agentPath,
      recent_runs: recentRuns,
      logs_directory: logsDir
    };
  }
}
