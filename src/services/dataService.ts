import axios from 'axios';
import Papa from 'papaparse';
import { Scholarship, RawScholarshipData } from '../types/scholarship';
import { parseDate } from '../utils/dateUtils';

/**
 * Service for fetching and processing scholarship data from Google Sheets
 */
class DataService {
  private readonly csvUrl: string;

  constructor(csvUrl?: string) {
    // Default to a sample URL - replace with your actual Google Sheets CSV URL
    this.csvUrl = csvUrl || process.env.REACT_APP_SHEETS_URL || '';
  }

  /**
   * Fetches scholarship data from Google Sheets CSV
   */
  async fetchScholarships(): Promise<Scholarship[]> {
    try {
      if (!this.csvUrl) {
        console.warn('No CSV URL provided, returning dummy data');
        return this.generateDummyData();
      }

      const response = await axios.get(this.csvUrl, {
        timeout: 10000,
        headers: {
          'Accept': 'text/csv',
        },
      });

      return this.parseCSVData(response.data);
    } catch (error) {
      console.error('Error fetching scholarship data:', error);
      // Fallback to dummy data for development
      return this.generateDummyData();
    }
  }

  /**
   * Parses CSV string data into Scholarship objects
   */
  private parseCSVData(csvData: string): Scholarship[] {
    const parseResult = Papa.parse<RawScholarshipData>(csvData, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (header: string) => header.trim(),
    });

    if (parseResult.errors.length > 0) {
      console.warn('CSV parsing errors:', parseResult.errors);
    }

    return parseResult.data
      .map((row, index) => this.transformRawData(row, index))
      .filter((scholarship): scholarship is Scholarship => scholarship !== null);
  }

  /**
   * Transforms raw CSV data into Scholarship object
   */
  private transformRawData(raw: RawScholarshipData, index: number): Scholarship | null {
    try {
      const deadline = parseDate(raw.Deadline);
      if (!deadline) {
        console.warn(`Invalid deadline for scholarship at row ${index + 1}:`, raw.Deadline);
        return null;
      }

      return {
        id: `scholarship-${index + 1}`,
        title: raw.Title?.trim() || 'Untitled Scholarship',
        description: raw.Description?.trim() || 'No description available',
        amount: raw.Amount?.trim() || 'Amount not specified',
        deadline,
        eligibility: this.parseArrayField(raw.Eligibility),
        requirements: this.parseArrayField(raw.Requirements),
        applicationUrl: raw['Application URL']?.trim() || '',
        provider: raw.Provider?.trim() || 'Unknown Provider',
        location: raw.Location?.trim() || 'Not specified',
        category: raw.Category?.trim() || 'General',
        isActive: raw.Status?.toLowerCase() !== 'inactive',
      };
    } catch (error) {
      console.error(`Error transforming row ${index + 1}:`, error, raw);
      return null;
    }
  }

  /**
   * Parses comma-separated string into array
   */
  private parseArrayField(field: string): string[] {
    if (!field) return [];
    return field
      .split(',')
      .map(item => item.trim())
      .filter(item => item.length > 0);
  }

  /**
   * Generates dummy data for development and testing
   */
  private generateDummyData(): Scholarship[] {
    const currentYear = new Date().getFullYear();
    
    return [
      {
        id: 'scholarship-1',
        title: 'Merit Excellence Scholarship',
        description: 'A prestigious scholarship for outstanding academic achievement in STEM fields. Recipients demonstrate exceptional performance in mathematics, science, and technology courses.',
        amount: '$5,000',
        deadline: new Date(currentYear, 11, 15), // December 15
        eligibility: ['Undergraduate students', 'GPA 3.5+', 'STEM majors'],
        requirements: ['Academic transcripts', 'Letter of recommendation', 'Personal essay'],
        applicationUrl: 'https://example.com/apply/merit',
        provider: 'STEM Education Foundation',
        location: 'United States',
        category: 'Academic Merit',
        isActive: true,
      },
      {
        id: 'scholarship-2',
        title: 'Community Impact Award',
        description: 'Supporting students who have made significant contributions to their communities through volunteer work and social initiatives.',
        amount: '$3,000',
        deadline: new Date(currentYear + 1, 0, 31), // January 31 next year
        eligibility: ['High school seniors', 'College students', 'Volunteer experience required'],
        requirements: ['Community service documentation', 'Personal statement', 'Reference letters'],
        applicationUrl: 'https://example.com/apply/community',
        provider: 'Community Leaders Foundation',
        location: 'Canada',
        category: 'Community Service',
        isActive: true,
      },
      {
        id: 'scholarship-3',
        title: 'Future Innovators Grant',
        description: 'Empowering the next generation of innovators and entrepreneurs with funding for education and startup initiatives.',
        amount: '$7,500',
        deadline: new Date(currentYear, 6, 1), // July 1 (past deadline for testing)
        eligibility: ['Graduate students', 'Entrepreneurial focus', 'Business or technology major'],
        requirements: ['Business plan', 'Academic records', 'Interview'],
        applicationUrl: 'https://example.com/apply/innovation',
        provider: 'Innovation Hub',
        location: 'Global',
        category: 'Entrepreneurship',
        isActive: false,
      },
      {
        id: 'scholarship-4',
        title: 'Diversity in Tech Scholarship',
        description: 'Promoting diversity and inclusion in technology fields by supporting underrepresented students pursuing computer science and engineering degrees.',
        amount: '$4,000',
        deadline: new Date(currentYear, 11, 1), // December 1
        eligibility: ['Underrepresented minorities', 'Computer Science majors', 'Engineering students'],
        requirements: ['Personal essay on diversity', 'Academic transcripts', 'Portfolio'],
        applicationUrl: 'https://example.com/apply/diversity-tech',
        provider: 'Tech Diversity Alliance',
        location: 'United States',
        category: 'Diversity & Inclusion',
        isActive: true,
      },
      {
        id: 'scholarship-5',
        title: 'Environmental Stewardship Award',
        description: 'Supporting students passionate about environmental conservation and sustainable development. Ideal for those studying environmental science, renewable energy, or related fields.',
        amount: '$6,000',
        deadline: new Date(currentYear, 9, 15), // October 15 (recently passed for testing)
        eligibility: ['Environmental science majors', 'Sustainability focus', 'All academic levels'],
        requirements: ['Research proposal', 'Environmental project portfolio', 'Faculty recommendation'],
        applicationUrl: 'https://example.com/apply/environment',
        provider: 'Green Future Foundation',
        location: 'International',
        category: 'Environmental',
        isActive: true,
      },
      {
        id: 'scholarship-6', 
        title: 'First-Generation College Student Support',
        description: 'Dedicated to supporting first-generation college students who are paving the way for their families in higher education.',
        amount: '$2,500',
        deadline: new Date(currentYear + 1, 1, 28), // February 28 next year
        eligibility: ['First-generation college students', 'Financial need demonstrated', 'All majors welcome'],
        requirements: ['FAFSA form', 'Personal statement', 'Financial documentation'],
        applicationUrl: 'https://example.com/apply/first-gen',
        provider: 'Educational Equity Foundation',
        location: 'United States',
        category: 'Need-Based',
        isActive: true,
      },
    ];
  }
}

// Create and export a singleton instance
export const dataService = new DataService();

// Export the class for testing purposes
export { DataService };
