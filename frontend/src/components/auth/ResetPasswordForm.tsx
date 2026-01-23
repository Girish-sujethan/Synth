/**
 * Password reset form component with email input and confirmation flow.
 */

import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { AuthError } from '../../types/auth';

interface ResetPasswordFormProps {
  onSuccess?: () => void;
  onError?: (error: AuthError) => void;
}

/**
 * Password reset form component for password recovery.
 */
export function ResetPasswordForm({ onSuccess, onError }: ResetPasswordFormProps) {
  const { resetPassword, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);

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

    const result = await resetPassword({ email });

    if (result.error) {
      if (onError) {
        onError(result.error);
      }
    } else {
      setSuccess(true);
      if (onSuccess) {
        onSuccess();
      }
    }
  };

  if (success) {
    return (
      <div className="reset-password-success">
        <p>Password reset email sent!</p>
        <p>Please check your email for instructions to reset your password.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="reset-password-form">
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

      {error && (
        <div className="error-message global-error">
          {error.message}
        </div>
      )}

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Sending...' : 'Send Reset Link'}
      </button>
    </form>
  );
}

