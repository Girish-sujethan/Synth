import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { BoardColumn } from '../components/KanbanBoard';

const API_BASE_URL = '/api';

const getAuthToken = () => {
  return localStorage.getItem('auth_token') || '';
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useColumns = (teamId: string) => {
  return useQuery({
    queryKey: ['columns', teamId],
    queryFn: async () => {
      const response = await apiClient.get(`/teams/${teamId}/columns`);
      return response.data.columns as BoardColumn[];
    },
    enabled: !!teamId,
  });
};

export const useUpdateColumn = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      columnKey,
      data,
    }: {
      columnKey: string;
      data: { display_name?: string; position?: number; wip_limit?: number | null };
    }) => {
      const response = await apiClient.patch(`/teams/${teamId}/columns/${columnKey}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['columns', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
    },
  });
};

export const useReorderColumns = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (orderedKeys: string[]) => {
      const response = await apiClient.put(`/teams/${teamId}/columns/reorder`, {
        ordered_keys: orderedKeys,
      });
      return response.data.columns;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['columns', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
    },
  });
};

export const useCreateColumn = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { key: string; display_name: string; position?: number; wip_limit?: number }) => {
      const response = await apiClient.post(`/teams/${teamId}/columns`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['columns', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
    },
  });
};

export const useDeleteColumn = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ columnKey, migrateTasksTo }: { columnKey: string; migrateTasksTo?: string }) => {
      await apiClient.delete(`/teams/${teamId}/columns/${columnKey}`, {
        data: migrateTasksTo ? { migrate_tasks_to: migrateTasksTo } : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['columns', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
    },
  });
};

export const useMoveTask = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      taskId,
      columnKey,
      note,
      clientAction,
    }: {
      taskId: string;
      columnKey: string;
      note?: string;
      clientAction?: string;
    }) => {
      const response = await apiClient.post(`/tasks/${taskId}/move?team_id=${teamId}`, {
        column_key: columnKey,
        note,
        client_action: clientAction,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
      queryClient.invalidateQueries({ queryKey: ['columns', teamId] });
    },
  });
};
