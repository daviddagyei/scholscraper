import { useState, useEffect } from 'react';
import type { Scholarship, LoadingState } from '../types/scholarship';
import { dataService } from '../services/dataService';

/**
 * Custom hook for managing scholarship data and categories
 */
export const useScholarships = () => {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    error: null,
  });

  /**
   * Fetches scholarship data and categories
   */
  const fetchData = async () => {
    setLoadingState({ isLoading: true, error: null });
    
    try {
      // Fetch scholarships and categories in parallel
      const [scholarshipData, categoryData] = await Promise.all([
        dataService.fetchScholarships(),
        dataService.fetchCategories()
      ]);
      
      setScholarships(scholarshipData);
      setCategories(categoryData);
      setLoadingState({ isLoading: false, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch data';
      setLoadingState({ isLoading: false, error: errorMessage });
    }
  };

  /**
   * Refreshes scholarship data and categories
   */
  const refreshData = () => {
    fetchData();
  };

  // Fetch data on mount
  useEffect(() => {
    fetchData();
  }, []);

  return {
    scholarships,
    categories,
    isLoading: loadingState.isLoading,
    error: loadingState.error,
    refreshData,
    // Keep the old method name for backward compatibility
    refreshScholarships: refreshData,
  };
};