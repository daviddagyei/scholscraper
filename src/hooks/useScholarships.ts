import { useState, useEffect } from 'react';
import { Scholarship, LoadingState } from '../types/scholarship';
import { dataService } from '../services/dataService';

/**
 * Custom hook for managing scholarship data
 */
export const useScholarships = () => {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    error: null,
  });

  /**
   * Fetches scholarship data
   */
  const fetchScholarships = async () => {
    setLoadingState({ isLoading: true, error: null });
    
    try {
      const data = await dataService.fetchScholarships();
      setScholarships(data);
      setLoadingState({ isLoading: false, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch scholarships';
      setLoadingState({ isLoading: false, error: errorMessage });
    }
  };

  /**
   * Refreshes scholarship data
   */
  const refreshScholarships = () => {
    fetchScholarships();
  };

  // Fetch data on mount
  useEffect(() => {
    fetchScholarships();
  }, []);

  return {
    scholarships,
    isLoading: loadingState.isLoading,
    error: loadingState.error,
    refreshScholarships,
  };
};
