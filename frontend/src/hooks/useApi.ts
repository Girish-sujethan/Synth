/**
 * useApi hook with TypeScript generics for type-safe API calls and state management.
 */

import { useState, useCallback } from "react";
import { ApiState, ApiRequestConfig, ApiResponse } from "@/types/api";
import { apiRequest } from "@/lib/api-client";
import { useApiContext } from "@/contexts/ApiContext";

/**
 * Custom hook for making API requests with loading, error, and success states.
 */
export function useApi<TData = unknown>() {
  const { defaultConfig } = useApiContext();
  const [state, setState] = useState<ApiState<TData>>({
    data: null,
    loading: false,
    error: null,
    success: false,
  });

  /**
   * Execute an API request.
   */
  const execute = useCallback(
    async (endpoint: string, config?: ApiRequestConfig): Promise<TData | null> => {
      setState({
        data: null,
        loading: true,
        error: null,
        success: false,
      });

      try {
        const finalConfig = { ...defaultConfig, ...config };
        const response: ApiResponse<TData> = await apiRequest<TData>(endpoint, finalConfig);

        if (response.success && response.data) {
          setState({
            data: response.data,
            loading: false,
            error: null,
            success: true,
          });
          return response.data;
        } else {
          const error = response.error || {
            message: "Request failed",
            type: "ApiError",
          };
          setState({
            data: null,
            loading: false,
            error,
            success: false,
          });
          return null;
        }
      } catch (error) {
        const apiError =
          error && typeof error === "object" && "message" in error
            ? (error as { message: string; type?: string })
            : { message: "An unexpected error occurred", type: "UnknownError" };

        setState({
          data: null,
          loading: false,
          error: {
            message: apiError.message,
            type: apiError.type || "UnknownError",
          },
          success: false,
        });
        return null;
      }
    },
    [defaultConfig]
  );

  /**
   * Reset the API state.
   */
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

