/**
 * Layout wrapper component with navigation and main content area.
 */

import { Outlet } from "react-router-dom";
import { Navigation } from "./Navigation";

/**
 * Layout component providing consistent page structure.
 */
export function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t bg-background py-4">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 Synth. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

