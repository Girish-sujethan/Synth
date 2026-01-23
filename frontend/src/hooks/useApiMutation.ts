/**
 * Mutation hook for POST, PUT, DELETE operations with optimistic updates.
 */

import { useState, useCallback } from "react";
import { ApiMutationResult, ApiRequestConfig } from "@/types/api";
import { apiPost, apiPut, apiPatch, apiDelete } from "@/lib/api-client";
import { useApiContext } from "@/contexts/ApiContext";

type HttpMethod = "POST" | "PUT" | "PATCH" | "DELETE";

interface UseApiMutationOptions extends ApiRequestConfig {
  /**
   * HTTP method to use.
   */
  method?: HttpMethod;

  /**
   * Optimistic update function.
   */
  onOptimisticUpdate?: (variables: unknown) => void;

  /**
   * Success callback.
   */
  onSuccess?: (data: unknown) => void;

  /**
   * Error callback.
   */
  onError?: (error: unknown) => void;
}

/**
 * Custom hook for mutation operations (POST, PUT, PATCH, DELETE).
 */
export function useApiMutation<TData = unknown, TVariables = unknown>(
  endpoint: string,
  options: UseApiMutationOptions = {}
): ApiMutationResult<TData, TVariables> {
  const { defaultConfig } = useApiContext();
  const { method = "POST", onOptimisticUpdate, onSuccess, onError, ...config } = options;

  const [state, setState] = useState<ApiMutationResult<TData, TVariables>>({
    data: null,
    loading: false,
    error: null,
    success: false,
    mutate: async () => null,
    reset: () => {},
  });

  /**
   * Execute the mutation.
   */
  const mutate = useCallback(
    async (variables: TVariables, mutateConfig?: ApiRequestConfig): Promise<TData | null> => {
      // Optimistic update
      if (onOptimisticUpdate) {
        onOptimisticUpdate(variables);
      }

      setState((prev) => ({
        ...prev,
        loading: true,
        error: null,
        success: false,
      }));

      try {
        const finalConfig = { ...defaultConfig, ...config, ...mutateConfig };
        let response;

        switch (method) {
          case "POST":
            response = await apiPost<TData, TVariables>(endpoint, variables, finalConfig);
            break;
          case "PUT":
            response = await apiPut<TData, TVariables>(endpoint, variables, finalConfig);
            break;
          case "PATCH":
            response = await apiPatch<TData, TVariables>(endpoint, variables, finalConfig);
            break;
          case "DELETE":
            response = await apiDelete<TData>(endpoint, finalConfig);
            break;
          default:
            throw new Error(`Unsupported HTTP method: ${method}`);
        }

        if (response.success && response.data) {
          setState((prev) => ({
            ...prev,
            data: response.data!,
            loading: false,
            error: null,
            success: true,
          }));

          if (onSuccess) {
            onSuccess(response.data);
          }

          return response.data;
        } else {
          const error = response.error || {
            message: "Request failed",
            type: "ApiError",
          };
          setState((prev) => ({
            ...prev,
            loading: false,
            error,
            success: false,
          }));

          if (onError) {
            onError(error);
          }

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
          error: {
            message: apiError.message,
            type: apiError.type || "UnknownError",
          },
          success: false,
        }));

        if (onError) {
          onError(apiError);
        }

        return null;
      }
    },
    [endpoint, method, defaultConfig, config, onOptimisticUpdate, onSuccess, onError]
  );

  /**
   * Reset mutation state.
   */
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false,
      mutate,
      reset,
    });
  }, [mutate]);

  return {
    ...state,
    mutate,
    reset,
  };
}

