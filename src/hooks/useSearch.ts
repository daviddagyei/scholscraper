import { useState, useMemo, useCallback } from 'react';
import { Scholarship, SearchFilters } from '../types/scholarship';
import { searchScholarships } from '../utils/searchUtils';
import { isDateInRange } from '../utils/dateUtils';

/**
 * Initial filter state
 */
const initialFilters: SearchFilters = {
  searchTerm: '',
  category: '',
  location: '',
  minAmount: 0,
  maxAmount: 100000,
  deadlineFrom: null,
  deadlineTo: null,
  eligibility: [],
};

/**
 * Custom hook for search and filtering functionality
 */
export const useSearch = (scholarships: Scholarship[]) => {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);

  /**
   * Updates search filters
   */
  const updateFilters = useCallback((newFilters: Partial<SearchFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  /**
   * Resets all filters to initial state
   */
  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, []);

  /**
   * Extracts unique values for filter options
   */
  const filterOptions = useMemo(() => {
    const categories = [...new Set(scholarships.map(s => s.category))].sort();
    const locations = [...new Set(scholarships.map(s => s.location))].sort();
    const eligibilityOptions = [...new Set(
      scholarships.flatMap(s => s.eligibility)
    )].sort();

    return {
      categories,
      locations,
      eligibilityOptions,
    };
  }, [scholarships]);

  /**
   * Parses amount string to number for comparison
   */
  const parseAmount = (amountStr: string): number => {
    const numStr = amountStr.replace(/[$,\s]/g, '');
    const num = parseFloat(numStr);
    return isNaN(num) ? 0 : num;
  };

  /**
   * Applies all filters to scholarships
   */
  const filteredScholarships = useMemo(() => {
    let result = scholarships;

    // Apply text search first
    if (filters.searchTerm.trim()) {
      result = searchScholarships(result, filters.searchTerm);
    }

    // Apply filters
    result = result.filter(scholarship => {
      // Category filter
      if (filters.category && scholarship.category !== filters.category) {
        return false;
      }

      // Location filter
      if (filters.location && scholarship.location !== filters.location) {
        return false;
      }

      // Amount range filter
      const amount = parseAmount(scholarship.amount);
      if (amount < filters.minAmount || amount > filters.maxAmount) {
        return false;
      }

      // Date range filter
      if (!isDateInRange(scholarship.deadline, filters.deadlineFrom, filters.deadlineTo)) {
        return false;
      }

      // Eligibility filter
      if (filters.eligibility.length > 0) {
        const hasMatchingEligibility = filters.eligibility.some(filterEligibility =>
          scholarship.eligibility.some(scholarshipEligibility =>
            scholarshipEligibility.toLowerCase().includes(filterEligibility.toLowerCase())
          )
        );
        if (!hasMatchingEligibility) {
          return false;
        }
      }

      return true;
    });

    // Sort by deadline (nearest first)
    return result.sort((a, b) => a.deadline.getTime() - b.deadline.getTime());
  }, [scholarships, filters]);

  /**
   * Search statistics
   */
  const searchStats = useMemo(() => ({
    totalScholarships: scholarships.length,
    filteredCount: filteredScholarships.length,
    hasActiveFilters: filters.searchTerm.trim() !== '' || 
                     filters.category !== '' || 
                     filters.location !== '' ||
                     filters.minAmount > 0 ||
                     filters.maxAmount < 100000 ||
                     filters.deadlineFrom !== null ||
                     filters.deadlineTo !== null ||
                     filters.eligibility.length > 0,
  }), [scholarships.length, filteredScholarships.length, filters]);

  return {
    filters,
    updateFilters,
    resetFilters,
    filteredScholarships,
    filterOptions,
    searchStats,
  };
};
