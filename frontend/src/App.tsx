import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TaskManagement } from './components/TaskManagement';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  // TODO: Get teamId and userRole from auth context
  const teamId = new URLSearchParams(window.location.search).get('team_id') || '';
  const userRole = (new URLSearchParams(window.location.search).get('role') as any) || 'member';

  if (!teamId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Team ID Required</h1>
          <p className="text-gray-600">
            Please provide a team_id query parameter: ?team_id=...
          </p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100">
        <TaskManagement teamId={teamId} userRole={userRole} />
      </div>
    </QueryClientProvider>
  );
}

export default App;
