/**
 * Query hook for GET operations with caching and refetch capabilities.
 */

import { useState, useEffect, useCallback } from "react";
import { ApiQueryResult, ApiRequestConfig } from "@/types/api";
import { apiGet } from "@/lib/api-client";
import { useApiContext } from "@/contexts/ApiContext";

interface UseApiQueryOptions extends ApiRequestConfig {
  /**
   * Whether to fetch immediately on mount.
   */
  enabled?: boolean;

  /**
   * Refetch interval in milliseconds.
   */
  refetchInterval?: number;
}

/**
 * Custom hook for GET operations with automatic fetching and refetching.
 */
export function useApiQuery<TData = unknown>(
  endpoint: string,
  options: UseApiQueryOptions = {}
): ApiQueryResult<TData> {
  const { defaultConfig } = useApiContext();
  const { enabled = true, refetchInterval, ...config } = options;

  const [state, setState] = useState<ApiQueryResult<TData>>({
    data: null,
    loading: enabled,
    error: null,
    success: false,
    isRefetching: false,
    refetch: async () => null,
  });

  /**
   * Fetch data from the API.
   */
  const fetchData = useCallback(
    async (isRefetch = false): Promise<TData | null> => {
      if (isRefetch) {
        setState((prev) => ({ ...prev, isRefetching: true }));
      } else {
        setState((prev) => ({ ...prev, loading: true, error: null }));
      }

      try {
        const finalConfig = { ...defaultConfig, ...config };
        const response = await apiGet<TData>(endpoint, finalConfig);

        if (response.success && response.data) {
          setState((prev) => ({
            ...prev,
            data: response.data!,
            loading: false,
            isRefetching: false,
            error: null,
            success: true,
          }));
          return response.data;
        } else {
          const error = response.error || {
            message: "Request failed",
            type: "ApiError",
          };
          setState((prev) => ({
            ...prev,
            loading: false,
            isRefetching: false,
            error,
            success: false,
          }));
          return null;
        }
      } catch (error) {
        const apiError =
          error && typeof error === "object" && "message" in error
            ? (error as { message: string; type?: string })
            : { message: "An unexpected error occurred", type: "UnknownError" };

        setState((prev) => ({
          ...prev,
          loading: false,
          isRefetching: false,
          error: {
            message: apiError.message,
            type: apiError.type || "UnknownError",
          },
          success: false,
        }));
        return null;
      }
    },
    [endpoint, defaultConfig, config]
  );

  /**
   * Refetch function.
   */
  const refetch = useCallback(
    async (refetchConfig?: ApiRequestConfig): Promise<TData | null> => {
      const mergedConfig = { ...config, ...refetchConfig };
      return fetchData(true);
    },
    [fetchData, config]
  );

  // Initial fetch
  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [enabled, fetchData]);

  // Refetch interval
  useEffect(() => {
    if (!refetchInterval || !enabled) {
      return;
    }

    const interval = setInterval(() => {
      fetchData(true);
    }, refetchInterval);

    return () => clearInterval(interval);
  }, [refetchInterval, enabled, fetchData]);

  return {
    ...state,
    refetch,
  };
}

