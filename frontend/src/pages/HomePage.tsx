/**
 * Home page component as the main landing page.
 */

import { useAuth } from "@/hooks/useAuth";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

/**
 * Home page component for authenticated users.
 */
export function HomePage() {
  const { user } = useAuth();

  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Welcome to Synth</CardTitle>
        </CardHeader>
        <CardContent>
          {user && (
            <div className="space-y-2">
              <p className="text-muted-foreground">
                Logged in as: <strong>{user.email}</strong>
              </p>
              {user.user_metadata && Object.keys(user.user_metadata).length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground">User Metadata:</p>
                  <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
                    {JSON.stringify(user.user_metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

