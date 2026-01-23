/**
 * Authentication utility functions for token validation and session management.
 */

import { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { AuthError } from '../types/auth';

/**
 * Check if a session is valid and not expired.
 */
export function isSessionValid(session: Session | null): boolean {
  if (!session) {
    return false;
  }

  const expiresAt = session.expires_at;
  if (!expiresAt) {
    return false;
  }

  // Check if session expires in the next 5 minutes (buffer time)
  const expiresIn = expiresAt * 1000 - Date.now();
  return expiresIn > 5 * 60 * 1000; // 5 minutes in milliseconds
}

/**
 * Get the current session from Supabase.
 */
export async function getCurrentSession(): Promise<Session | null> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error('Error getting session:', error);
      return null;
    }
    
    return session;
  } catch (error) {
    console.error('Error getting session:', error);
    return null;
  }
}

/**
 * Get the current user from Supabase.
 */
export async function getCurrentUser() {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error('Error getting user:', error);
      return null;
    }
    
    return user;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
}

/**
 * Create an AuthError from a Supabase error.
 */
export function createAuthError(error: any): AuthError {
  // Extract more detailed error information
  let message = error.message || 'An authentication error occurred';
  
  // Handle specific Supabase error codes
  if (error.code) {
    switch (error.code) {
      case 'signup_disabled':
        message = 'Sign up is currently disabled. Please contact support.';
        break;
      case 'email_not_confirmed':
        message = 'Please check your email to confirm your account.';
        break;
      case 'user_already_registered':
        message = 'An account with this email already exists. Please sign in instead.';
        break;
      case 'invalid_email':
        message = 'Please enter a valid email address.';
        break;
      case 'weak_password':
        message = 'Password is too weak. Please use a stronger password.';
        break;
      case 'over_email_send_rate_limit':
        message = 'Too many emails have been sent. Please wait a few minutes before trying again.';
        break;
      default:
        // Use the error message as-is
        break;
    }
  }
  
  return {
    message,
    code: error.code,
    status: error.status,
  };
}

/**
 * Clear authentication data from storage.
 */
export async function clearAuthData(): Promise<void> {
  try {
    await supabase.auth.signOut();
  } catch (error) {
    console.error('Error clearing auth data:', error);
  }
}

