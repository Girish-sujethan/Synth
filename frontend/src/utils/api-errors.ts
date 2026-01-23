/**
 * Error handling utilities for API responses and user-friendly error messages.
 */

import { ApiError } from "@/types/api";

/**
 * Create an API error from a Response object.
 */
export async function createApiErrorFromResponse(response: Response): Promise<ApiError> {
  let errorData: unknown;

  try {
    errorData = await response.json();
  } catch {
    // If response is not JSON, use status text
    errorData = { message: response.statusText };
  }

  const error = errorData as { error?: { message?: string; type?: string; details?: unknown } };

  return {
    message: error?.error?.message || response.statusText || "An error occurred",
    type: error?.error?.type || "ApiError",
    status: response.status,
    code: response.status.toString(),
    details: error?.error?.details as Record<string, unknown> | undefined,
  };
}

/**
 * Create an API error from a generic error.
 */
export function createApiErrorFromError(error: unknown): ApiError {
  if (error instanceof Error) {
    return {
      message: error.message,
      type: error.name,
    };
  }

  if (typeof error === "string") {
    return {
      message: error,
      type: "Error",
    };
  }

  return {
    message: "An unexpected error occurred",
    type: "UnknownError",
  };
}

/**
 * Get user-friendly error message.
 */
export function getUserFriendlyErrorMessage(error: ApiError): string {
  // Map common error types to user-friendly messages
  const errorMessages: Record<string, string> = {
    ValidationError: "Please check your input and try again",
    AuthenticationError: "Please sign in to continue",
    AuthorizationError: "You don't have permission to perform this action",
    NotFoundError: "The requested resource was not found",
    NetworkError: "Network error. Please check your connection",
    TimeoutError: "Request timed out. Please try again",
  };

  // Check if we have a mapped message
  if (error.type && errorMessages[error.type]) {
    return errorMessages[error.type];
  }

  // Use the error message if available
  if (error.message) {
    return error.message;
  }

  return "An error occurred. Please try again";
}

/**
 * Check if error is a network error.
 */
export function isNetworkError(error: ApiError): boolean {
  return error.type === "NetworkError" || error.type === "TypeError";
}

/**
 * Check if error is an authentication error.
 */
export function isAuthenticationError(error: ApiError): boolean {
  return error.status === 401 || error.type === "AuthenticationError";
}

/**
 * Check if error is an authorization error.
 */
export function isAuthorizationError(error: ApiError): boolean {
  return error.status === 403 || error.type === "AuthorizationError";
}

