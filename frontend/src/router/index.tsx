/**
 * Router configuration with route definitions and protected route logic.
 */

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ApiProvider } from "@/contexts/ApiContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Layout } from "@/components/layout/Layout";
import { HomePage } from "@/pages/HomePage";
import { TasksPage } from "@/pages/TasksPage";
import { LoginPage } from "@/pages/LoginPage";
import { SignUpPage } from "@/pages/SignUpPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ResetPasswordForm } from "@/components/auth/ResetPasswordForm";

/**
 * Main router configuration.
 * Defines all routes in the application with their protection and layout.
 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <ApiProvider>
        <AuthProvider>
          <Layout />
        </AuthProvider>
      </ApiProvider>
    ),
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        ),
      },
      {
        path: "tasks",
        element: (
          <ProtectedRoute>
            <TasksPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "signup",
        element: <SignUpPage />,
      },
      {
        path: "reset-password",
        element: (
          <div className="auth-page">
            <h1>Reset Password</h1>
            <ResetPasswordForm />
          </div>
        ),
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);

/**
 * Router provider component.
 * Renders the router with all configured routes.
 */
export function AppRouter() {
  return <RouterProvider router={router} />;
}

