/**
 * TypeScript interfaces for route parameters, navigation state, and route guards.
 */

import { Location } from "react-router-dom";

/**
 * Route parameter types for type-safe route parameters.
 */
export interface RouteParams {
  [key: string]: string | undefined;
}

/**
 * Navigation state that can be passed between routes.
 */
export interface NavigationState {
  from?: Location;
  message?: string;
  [key: string]: unknown;
}

/**
 * Route guard configuration.
 */
export interface RouteGuard {
  /**
   * Whether the route requires authentication.
   */
  requireAuth?: boolean;

  /**
   * Whether the route requires no authentication (redirects if authenticated).
   */
  requireGuest?: boolean;

  /**
   * Required permissions for accessing the route.
   */
  permissions?: string[];

  /**
   * Redirect path if guard fails.
   */
  redirectTo?: string;
}

/**
 * Route configuration interface.
 */
export interface RouteConfig {
  path: string;
  element: React.ComponentType;
  guard?: RouteGuard;
  children?: RouteConfig[];
}

