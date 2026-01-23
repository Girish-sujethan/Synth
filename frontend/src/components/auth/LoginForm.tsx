/**
 * Login form component with email/password inputs and validation.
 */

import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { AuthError } from '../../types/auth';

interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: AuthError) => void;
}

/**
 * Login form component for user authentication.
 */
export function LoginForm({ onSuccess, onError }: LoginFormProps) {
  const { signIn, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

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

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const result = await signIn({ email, password });

    if (result.error) {
      if (onError) {
        onError(result.error);
      }
    } else {
      if (onSuccess) {
        onSuccess();
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
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

      {error && (
        <div className="error-message global-error">
          {error.message}
        </div>
      )}

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
}

