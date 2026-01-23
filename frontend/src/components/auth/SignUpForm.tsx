/**
 * Sign-up form component with email/password confirmation and validation.
 */

import React, { useState, FormEvent, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { AuthError } from '../../types/auth';

interface SignUpFormProps {
  onSuccess?: () => void;
  onError?: (error: AuthError) => void;
}

/**
 * Sign-up form component for user registration.
 */
export function SignUpForm({ onSuccess, onError }: SignUpFormProps) {
  const { signUp, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirmation, setPasswordConfirmation] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const isSubmittingRef = useRef(false);

  /**
   * Validate form inputs.
   */
  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    if (!passwordConfirmation) {
      errors.passwordConfirmation = 'Please confirm your password';
    } else if (password !== passwordConfirmation) {
      errors.passwordConfirmation = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    e.stopPropagation();

    // Prevent double submission
    if (isSubmittingRef.current || loading) {
      console.warn('Signup form: Submission already in progress, ignoring duplicate submit');
      return;
    }

    if (!validate()) {
      return;
    }

    // Trim email before sending
    const trimmedEmail = email.trim();
    setSuccessMessage(null);
    isSubmittingRef.current = true;

    console.log('Signup form: Starting signup request for', trimmedEmail);

    try {
      const result = await signUp({
        email: trimmedEmail,
        password,
        passwordConfirmation,
      });

      if (result.error) {
        // Log error details for debugging
        console.error('Sign up error:', result.error);
        if (onError) {
          onError(result.error);
        }
      } else {
        // Check if email confirmation is required
        // If signup succeeded but no session, user needs to confirm email
        setSuccessMessage(
          'Account created successfully! Please check your email to confirm your account.'
        );
        // Don't call onSuccess immediately if email confirmation is required
        // Wait a bit to show the message, then redirect
        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          }
        }, 2000);
      }
    } finally {
      isSubmittingRef.current = false;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="signup-form">
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={loading}
          className={validationErrors.email ? 'error' : ''}
          placeholder="Enter your email"
        />
        {validationErrors.email && (
          <span className="error-message">{validationErrors.email}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
          className={validationErrors.password ? 'error' : ''}
          placeholder="Enter your password"
        />
        {validationErrors.password && (
          <span className="error-message">{validationErrors.password}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="passwordConfirmation">Confirm Password</label>
        <input
          type="password"
          id="passwordConfirmation"
          value={passwordConfirmation}
          onChange={(e) => setPasswordConfirmation(e.target.value)}
          disabled={loading}
          className={validationErrors.passwordConfirmation ? 'error' : ''}
          placeholder="Confirm your password"
        />
        {validationErrors.passwordConfirmation && (
          <span className="error-message">{validationErrors.passwordConfirmation}</span>
        )}
      </div>

      {error && (
        <div className="error-message global-error">
          {error.message}
          {error.code === 'over_email_send_rate_limit' && (
            <div className="text-xs mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
              <strong>Note:</strong> Email rate limit exceeded. For development, you can:
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>Disable email confirmation in Supabase Dashboard → Authentication → Settings</li>
                <li>Wait 5-10 minutes for the rate limit to reset</li>
                <li>Use a different email address for testing</li>
              </ul>
            </div>
          )}
          {error.code && error.code !== 'over_email_send_rate_limit' && (
            <span className="text-xs block mt-1">Error code: {error.code}</span>
          )}
        </div>
      )}

      {successMessage && !error && (
        <div className="success-message" style={{ color: 'green', padding: '10px', marginBottom: '10px' }}>
          {successMessage}
        </div>
      )}

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Creating account...' : 'Sign Up'}
      </button>
    </form>
  );
}

