/**
 * TypeScript interfaces for API responses, errors, and request configurations.
 */

/**
 * Standard API response structure.
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: ApiError;
}

/**
 * API error structure.
 */
export interface ApiError {
  message: string;
  type?: string;
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
}

/**
 * Request configuration options.
 */
export interface ApiRequestConfig extends RequestInit {
  /**
   * Whether to include authentication token.
   */
  requireAuth?: boolean;

  /**
   * Custom headers to include.
   */
  headers?: HeadersInit;

  /**
   * Request timeout in milliseconds.
   */
  timeout?: number;

  /**
   * Whether to retry on failure.
   */
  retry?: boolean;

  /**
   * Maximum number of retry attempts.
   */
  maxRetries?: number;
}

/**
 * API hook state.
 */
export interface ApiState<T = unknown> {
  /**
   * Response data.
   */
  data: T | null;

  /**
   * Loading state.
   */
  loading: boolean;

  /**
   * Error state.
   */
  error: ApiError | null;

  /**
   * Whether the request was successful.
   */
  success: boolean;
}

/**
 * API mutation result.
 */
export interface ApiMutationResult<TData = unknown, TVariables = unknown> extends ApiState<TData> {
  /**
   * Execute the mutation.
   */
  mutate: (variables: TVariables, config?: ApiRequestConfig) => Promise<TData | null>;

  /**
   * Reset the mutation state.
   */
  reset: () => void;
}

/**
 * API query result.
 */
export interface ApiQueryResult<TData = unknown> extends ApiState<TData> {
  /**
   * Refetch the query.
   */
  refetch: (config?: ApiRequestConfig) => Promise<TData | null>;

  /**
   * Whether the query is currently refetching.
   */
  isRefetching: boolean;
}

