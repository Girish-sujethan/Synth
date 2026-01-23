/**
 * Retry utility with exponential backoff for failed requests.
 */

/**
 * Retry configuration.
 */
export interface RetryConfig {
  /**
   * Maximum number of retry attempts.
   */
  maxRetries: number;

  /**
   * Initial delay in milliseconds.
   */
  retryDelay: number;

  /**
   * HTTP status codes that should trigger a retry.
   */
  retryOn: number[];

  /**
   * Whether to use exponential backoff.
   */
  exponentialBackoff?: boolean;
}

/**
 * Default retry configuration.
 */
const DEFAULT_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryOn: [408, 429, 500, 502, 503, 504],
  exponentialBackoff: true,
};

/**
 * Calculate delay for retry with exponential backoff.
 */
function calculateDelay(attempt: number, baseDelay: number, exponential: boolean): number {
  if (!exponential) {
    return baseDelay;
  }
  return baseDelay * Math.pow(2, attempt);
}

/**
 * Sleep for specified milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if an error should trigger a retry.
 */
function shouldRetry(error: unknown, retryOn: number[]): boolean {
  if (error instanceof Response) {
    return retryOn.includes(error.status);
  }
  // Retry on network errors
  if (error instanceof TypeError && error.message.includes("fetch")) {
    return true;
  }
  return false;
}

/**
 * Retry a function with exponential backoff.
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  let lastError: unknown;

  for (let attempt = 0; attempt <= finalConfig.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on last attempt
      if (attempt === finalConfig.maxRetries) {
        throw error;
      }

      // Check if error should trigger retry
      if (!shouldRetry(error, finalConfig.retryOn)) {
        throw error;
      }

      // Calculate delay and wait
      const delay = calculateDelay(
        attempt,
        finalConfig.retryDelay,
        finalConfig.exponentialBackoff ?? true
      );
      await sleep(delay);
    }
  }

  throw lastError;
}

