import Fuse from 'fuse.js';
import { Scholarship } from '../types/scholarship';

/**
 * Configuration for fuzzy search
 */
const fuseOptions: Fuse.IFuseOptions<Scholarship> = {
  keys: [
    { name: 'title', weight: 0.4 },
    { name: 'description', weight: 0.3 },
    { name: 'provider', weight: 0.2 },
    { name: 'category', weight: 0.1 },
  ],
  threshold: 0.3, // Lower = more strict matching
  includeScore: true,
  includeMatches: true,
  minMatchCharLength: 2,
};

/**
 * Creates a Fuse.js instance for fuzzy searching
 */
export const createSearchEngine = (scholarships: Scholarship[]): Fuse<Scholarship> => {
  return new Fuse(scholarships, fuseOptions);
};

/**
 * Performs fuzzy search on scholarships
 */
export const searchScholarships = (
  scholarships: Scholarship[],
  searchTerm: string
): Scholarship[] => {
  if (!searchTerm.trim()) {
    return scholarships;
  }

  const fuse = createSearchEngine(scholarships);
  const results = fuse.search(searchTerm);
  
  return results.map(result => result.item);
};

/**
 * Highlights search matches in text
 */
export const highlightMatches = (
  text: string,
  searchTerm: string,
  className: string = 'highlight'
): string => {
  if (!searchTerm.trim()) {
    return text;
  }

  const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
  return text.replace(regex, `<span class="${className}">$1</span>`);
};

/**
 * Escapes special regex characters
 */
const escapeRegExp = (string: string): string => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

/**
 * Extracts keywords from a search term
 */
export const extractKeywords = (searchTerm: string): string[] => {
  return searchTerm
    .toLowerCase()
    .split(/\s+/)
    .filter(word => word.length > 1)
    .map(word => word.trim());
};

/**
 * Calculates search relevance score
 */
export const calculateRelevanceScore = (
  scholarship: Scholarship,
  searchTerm: string
): number => {
  const keywords = extractKeywords(searchTerm);
  let score = 0;

  keywords.forEach(keyword => {
    const titleMatch = scholarship.title.toLowerCase().includes(keyword);
    const descMatch = scholarship.description.toLowerCase().includes(keyword);
    const providerMatch = scholarship.provider.toLowerCase().includes(keyword);
    const categoryMatch = scholarship.category.toLowerCase().includes(keyword);

    if (titleMatch) score += 4;
    if (descMatch) score += 2;
    if (providerMatch) score += 1;
    if (categoryMatch) score += 1;
  });

  return score;
};
