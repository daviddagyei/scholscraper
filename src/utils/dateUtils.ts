import { format, parse, isValid, isBefore, isAfter, parseISO } from 'date-fns';

/**
 * Formats a date for display
 */
export const formatDate = (date: Date): string => {
  return format(date, 'MMM dd, yyyy');
};

/**
 * Formats a date for deadline display with urgency indication
 */
export const formatDeadline = (date: Date): { text: string; isUrgent: boolean } => {
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { text: 'Expired', isUrgent: true };
  } else if (diffDays === 0) {
    return { text: 'Due today', isUrgent: true };
  } else if (diffDays <= 7) {
    return { text: `${diffDays} day${diffDays === 1 ? '' : 's'} left`, isUrgent: true };
  } else if (diffDays <= 30) {
    return { text: `${diffDays} days left`, isUrgent: false };
  } else {
    return { text: formatDate(date), isUrgent: false };
  }
};

/**
 * Parses various date formats from CSV data
 */
export const parseDate = (dateString: string): Date | null => {
  if (!dateString || dateString.trim() === '') {
    return null;
  }

  const trimmed = dateString.trim();
  
  // Try different date formats
  const formats = [
    'yyyy-MM-dd',
    'MM/dd/yyyy',
    'dd/MM/yyyy',
    'MMM dd, yyyy',
    'MMMM dd, yyyy',
    'yyyy/MM/dd',
  ];

  // Try ISO format first
  try {
    const isoDate = parseISO(trimmed);
    if (isValid(isoDate)) {
      return isoDate;
    }
  } catch {
    // Continue with other formats
  }

  // Try each format
  for (const formatStr of formats) {
    try {
      const parsed = parse(trimmed, formatStr, new Date());
      if (isValid(parsed)) {
        return parsed;
      }
    } catch {
      // Continue with next format
    }
  }

  console.warn(`Could not parse date: ${dateString}`);
  return null;
};

/**
 * Checks if a deadline is within a date range
 */
export const isDateInRange = (
  date: Date,
  from: Date | null,
  to: Date | null
): boolean => {
  if (from && isBefore(date, from)) {
    return false;
  }
  if (to && isAfter(date, to)) {
    return false;
  }
  return true;
};

/**
 * Sorts dates in ascending order (earliest first)
 */
export const sortByDeadline = (a: Date, b: Date): number => {
  return a.getTime() - b.getTime();
};
