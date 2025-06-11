import axios from 'axios';
import type { Scholarship } from '../types/scholarship';

/**
 * API Response interface matching backend format
 */
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

/**
 * Service for fetching scholarship data from the backend API
 */
class DataService {
  private readonly apiBaseUrl: string;
  private readonly axiosInstance;

  constructor() {
    this.apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';
    
    // Create axios instance with default configuration
    this.axiosInstance = axios.create({
      baseURL: this.apiBaseUrl,
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Fetches scholarship data from the backend API
   */
  async fetchScholarships(): Promise<Scholarship[]> {
    try {
      const response = await this.axiosInstance.get<ApiResponse<Scholarship[]>>('/api/public/scholarships');
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to fetch scholarships');
      }

      // Transform dates from string to Date objects
      const scholarships = response.data.data.map(scholarship => ({
        ...scholarship,
        deadline: new Date(scholarship.deadline)
      }));

      console.log(`✅ Fetched ${scholarships.length} scholarships from API`);
      
      if (scholarships.length > 0) {
        console.log('📄 Sample scholarship:', scholarships[0].title);
        if (scholarships[0].title === 'Tech Excellence Scholarship') {
          console.log('🎯 SUCCESS: Receiving LIVE data from Google Sheets!');
        }
      }
      
      return scholarships;
    } catch (error: any) {
      console.error('❌ Error fetching scholarship data from API:', error);
      console.error('❌ Full error details:', {
        message: error?.message,
        stack: error?.stack,
        response: error?.response?.data,
        status: error?.response?.status
      });
      
      // If API fails, return dummy data for development
      console.warn('⚠️ Falling back to dummy data due to API error');
      return this.generateDummyData();
    }
  }

  /**
   * Fetches available scholarship categories from the backend
   */
  async fetchCategories(): Promise<string[]> {
    try {
      const response = await this.axiosInstance.get<ApiResponse<string[]>>('/api/public/categories');
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to fetch categories');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error fetching categories from API:', error);
      
      // Return default categories as fallback
      return [
        'Academic Merit',
        'Community Service', 
        'Entrepreneurship',
        'Diversity & Inclusion',
        'Environmental',
        'Need-Based',
        'STEM',
        'Arts & Humanities'
      ];
    }
  }

  /**
   * Generates dummy data for development and testing when API is unavailable
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
        location: 'United States',
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
        location: 'United States',
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
        location: 'United States',
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