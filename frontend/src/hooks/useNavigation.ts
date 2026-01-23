/**
 * Custom hook for programmatic navigation and route information.
 */

import { useNavigate, useLocation, useParams, useSearchParams } from "react-router-dom";
import { NavigationState } from "@/router/types";

/**
 * Custom hook for navigation utilities.
 * 
 * Provides convenient methods for programmatic navigation and route information.
 */
export function useNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  /**
   * Navigate to a route.
   */
  const goTo = (path: string, state?: NavigationState) => {
    navigate(path, { state });
  };

  /**
   * Navigate back in history.
   */
  const goBack = () => {
    navigate(-1);
  };

  /**
   * Navigate forward in history.
   */
  const goForward = () => {
    navigate(1);
  };

  /**
   * Replace current route.
   */
  const replace = (path: string, state?: NavigationState) => {
    navigate(path, { replace: true, state });
  };

  /**
   * Get query parameter value.
   */
  const getQueryParam = (key: string): string | null => {
    return searchParams.get(key);
  };

  /**
   * Set query parameter.
   */
  const setQueryParam = (key: string, value: string) => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set(key, value);
    setSearchParams(newSearchParams);
  };

  /**
   * Remove query parameter.
   */
  const removeQueryParam = (key: string) => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete(key);
    setSearchParams(newSearchParams);
  };

  /**
   * Get all query parameters as object.
   */
  const getAllQueryParams = (): Record<string, string> => {
    const params: Record<string, string> = {};
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
    return params;
  };

  return {
    // Navigation methods
    goTo,
    goBack,
    goForward,
    replace,
    // Route information
    location,
    params,
    pathname: location.pathname,
    // Query parameter methods
    getQueryParam,
    setQueryParam,
    removeQueryParam,
    getAllQueryParams,
    searchParams,
  };
}

