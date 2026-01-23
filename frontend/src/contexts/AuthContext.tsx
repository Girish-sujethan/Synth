/**
 * React context for authentication state management.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Session, User as SupabaseUser } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { AuthState, AuthError, User, Session as AppSession } from '../types/auth';
import { createAuthError } from '../utils/auth';

interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signUp: (email: string, password: string, metadata?: Record<string, any>) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication context provider component.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<AppSession | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<AuthError | null>(null);

  /**
   * Initialize authentication state from existing session.
   */
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setSession(session as AppSession);
        setUser(session.user as User);
      }
      setLoading(false);
    });

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setSession(session as AppSession);
        setUser(session.user as User);
        setError(null);
      } else {
        setSession(null);
        setUser(null);
      }
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  /**
   * Sign in with email and password.
   */
  const signIn = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) {
        const error = createAuthError(authError);
        setError(error);
        return { error };
      }

      if (data.session) {
        setSession(data.session as AppSession);
        setUser(data.user as User);
      }

      return { error: null };
    } catch (err: any) {
      const error = createAuthError(err);
      setError(error);
      return { error };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Sign up with email and password.
   */
  const signUp = async (
    email: string,
    password: string,
    metadata?: Record<string, any>
  ) => {
    try {
      setLoading(true);
      setError(null);

      // Trim email to remove any whitespace
      const trimmedEmail = email.trim();

      console.log('[AuthContext] signUp called:', {
        email: trimmedEmail,
        timestamp: new Date().toISOString(),
      });

      const { data, error: authError } = await supabase.auth.signUp({
        email: trimmedEmail,
        password,
        options: {
          data: metadata,
          emailRedirectTo: `${window.location.origin}/`,
        },
      });

      console.log('[AuthContext] signUp response:', {
        hasError: !!authError,
        hasUser: !!data?.user,
        hasSession: !!data?.session,
        errorCode: authError?.code,
      });

      if (authError) {
        // Log full error for debugging
        console.error('Supabase signup error:', {
          message: authError.message,
          code: authError.code,
          status: authError.status,
          name: authError.name,
        });
        const error = createAuthError(authError);
        setError(error);
        return { error };
      }

      // Handle email confirmation flow
      // If email confirmation is required, Supabase may not return a session immediately
      if (data.session) {
        setSession(data.session as AppSession);
        setUser(data.user as User);
      } else if (data.user && !data.session) {
        // User created but needs email confirmation
        // Don't set session, but also don't treat as error
        // The user will need to confirm their email
        return { error: null };
      }

      return { error: null };
    } catch (err: any) {
      const error = createAuthError(err);
      setError(error);
      return { error };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Sign out the current user.
   */
  const signOut = async () => {
    try {
      setLoading(true);
      setError(null);

      const { error: authError } = await supabase.auth.signOut();

      if (authError) {
        const error = createAuthError(authError);
        setError(error);
        throw error;
      }

      setSession(null);
      setUser(null);
    } catch (err: any) {
      const error = createAuthError(err);
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset password by sending reset email.
   */
  const resetPassword = async (email: string) => {
    try {
      setLoading(true);
      setError(null);

      const { error: authError } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (authError) {
        const error = createAuthError(authError);
        setError(error);
        return { error };
      }

      return { error: null };
    } catch (err: any) {
      const error = createAuthError(err);
      setError(error);
      return { error };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Refresh the current session.
   */
  const refreshSession = async () => {
    try {
      const { data: { session }, error: authError } = await supabase.auth.refreshSession();

      if (authError) {
        const error = createAuthError(authError);
        setError(error);
        return;
      }

      if (session) {
        setSession(session as AppSession);
        setUser(session.user as User);
      }
    } catch (err: any) {
      const error = createAuthError(err);
      setError(error);
    }
  };

  const value: AuthContextType = {
    user,
    session,
    loading,
    error,
    signIn,
    signUp,
    signOut,
    resetPassword,
    refreshSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook to access authentication context.
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

