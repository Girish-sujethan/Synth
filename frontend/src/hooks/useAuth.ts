/**
 * Custom hook for authentication operations with loading states and error handling.
 */

import { useState } from 'react';
import { useAuth as useAuthContext } from '../contexts/AuthContext';
import { AuthError, SignInCredentials, SignUpCredentials, PasswordResetRequest } from '../types/auth';

interface UseAuthReturn {
  // State
  user: ReturnType<typeof useAuthContext>['user'];
  session: ReturnType<typeof useAuthContext>['session'];
  loading: boolean;
  error: AuthError | null;
  isAuthenticated: boolean;

  // Actions
  signIn: (credentials: SignInCredentials) => Promise<{ error: AuthError | null }>;
  signUp: (credentials: SignUpCredentials) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (request: PasswordResetRequest) => Promise<{ error: AuthError | null }>;
  refreshSession: () => Promise<void>;
  clearError: () => void;
}

/**
 * Custom hook for authentication operations.
 * 
 * Provides a convenient interface for authentication with loading states and error handling.
 */
export function useAuth(): UseAuthReturn {
  const authContext = useAuthContext();
  const [actionLoading, setActionLoading] = useState(false);

  const isAuthenticated = authContext.user !== null && authContext.session !== null;

  const signIn = async (credentials: SignInCredentials) => {
    setActionLoading(true);
    try {
      const result = await authContext.signIn(credentials.email, credentials.password);
      return result;
    } finally {
      setActionLoading(false);
    }
  };

  const signUp = async (credentials: SignUpCredentials) => {
    if (actionLoading) {
      console.warn('[useAuth] signUp called while already loading, ignoring duplicate call');
      return { error: { message: 'Signup already in progress', code: 'duplicate_request' } as AuthError };
    }
    setActionLoading(true);
    try {
      console.log('[useAuth] signUp wrapper called for:', credentials.email);
      const result = await authContext.signUp(
        credentials.email,
        credentials.password,
        credentials.metadata
      );
      return result;
    } finally {
      setActionLoading(false);
    }
  };

  const signOut = async () => {
    setActionLoading(true);
    try {
      await authContext.signOut();
    } finally {
      setActionLoading(false);
    }
  };

  const resetPassword = async (request: PasswordResetRequest) => {
    setActionLoading(true);
    try {
      const result = await authContext.resetPassword(request.email);
      return result;
    } finally {
      setActionLoading(false);
    }
  };

  const refreshSession = async () => {
    setActionLoading(true);
    try {
      await authContext.refreshSession();
    } finally {
      setActionLoading(false);
    }
  };

  const clearError = () => {
    // Note: Error clearing would need to be added to AuthContext if needed
  };

  return {
    user: authContext.user,
    session: authContext.session,
    loading: authContext.loading || actionLoading,
    error: authContext.error,
    isAuthenticated,
    signIn,
    signUp,
    signOut,
    resetPassword,
    refreshSession,
    clearError,
  };
}

