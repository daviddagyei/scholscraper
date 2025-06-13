import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

interface AgentResult {
  success: boolean;
  scholarships_discovered?: number;
  scholarships_saved?: number;
  error?: string;
  output?: string;
}

export class ScholarshipAgentController {
  private agentPath: string;

  constructor() {
    this.agentPath = path.join(__dirname, '../../langgraph-agent/backend/run_agent.py');
  }

  /**
   * Run the scholarship discovery agent
   */
  async runDiscovery(searchCriteria?: string): Promise<AgentResult> {
    return new Promise((resolve) => {
      const args = ['--daily'];
      if (searchCriteria) {
        args.push('--search', searchCriteria);
      }

      // Add timestamp for output file
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const outputFile = path.join(__dirname, `../../langgraph-agent/backend/logs/discovery_${timestamp}.json`);
      args.push('--output', outputFile);

      console.log(`Running scholarship agent with args: ${args.join(' ')}`);

      const pythonProcess = spawn('python3', [this.agentPath, ...args], {
        cwd: path.dirname(this.agentPath),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        console.log(`Scholarship agent process finished with code: ${code}`);
        
        if (code === 0) {
          // Try to read the output file for detailed results
          try {
            if (fs.existsSync(outputFile)) {
              const resultData = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
              resolve({
                success: true,
                scholarships_discovered: resultData.scholarships_discovered || 0,
                scholarships_saved: resultData.scholarships_saved || 0,
                output: stdout
              });
            } else {
              resolve({
                success: true,
                output: stdout
              });
            }
          } catch (error) {
            resolve({
              success: true,
              output: stdout,
              error: `Could not parse result file: ${error}`
            });
          }
        } else {
          resolve({
            success: false,
            error: `Agent failed with exit code ${code}. stderr: ${stderr}`,
            output: stdout
          });
        }
      });

      pythonProcess.on('error', (error) => {
        resolve({
          success: false,
          error: `Failed to start agent: ${error.message}`
        });
      });
    });
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
