/**
 * TypeScript interfaces for authentication-related data structures.
 */

import { User as SupabaseUser, Session as SupabaseSession } from '@supabase/supabase-js';

/**
 * Application user interface extending Supabase user.
 */
export interface User extends SupabaseUser {
  email?: string;
  user_metadata?: Record<string, any>;
  app_metadata?: Record<string, any>;
}

/**
 * Application session interface extending Supabase session.
 */
export interface Session extends SupabaseSession {
  user: User;
}

/**
 * Authentication state interface.
 */
export interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: AuthError | null;
}

/**
 * Authentication error interface.
 */
export interface AuthError {
  message: string;
  code?: string;
  status?: number;
}

/**
 * Sign in credentials.
 */
export interface SignInCredentials {
  email: string;
  password: string;
}

/**
 * Sign up credentials.
 */
export interface SignUpCredentials {
  email: string;
  password: string;
  passwordConfirmation?: string;
  metadata?: Record<string, any>;
}

/**
 * Password reset request.
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Password reset confirmation.
 */
export interface PasswordResetConfirmation {
  password: string;
  token: string;
}

