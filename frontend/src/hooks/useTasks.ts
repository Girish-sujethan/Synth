import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Task, TaskCreateRequest, TaskUpdateRequest } from '../types/task';

const API_BASE_URL = '/api';

// Get auth token from storage or context
const getAuthToken = () => {
  // TODO: Get from auth context or storage
  return localStorage.getItem('auth_token') || '';
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useTasks = (teamId: string) => {
  return useQuery({
    queryKey: ['tasks', teamId],
    queryFn: async () => {
      const response = await apiClient.get(`/board?team_id=${teamId}`);
      return response.data;
    },
    enabled: !!teamId,
  });
};

export const useTask = (taskId: string, teamId: string) => {
  return useQuery({
    queryKey: ['task', taskId, teamId],
    queryFn: async () => {
      const response = await apiClient.get(`/tasks/${taskId}?team_id=${teamId}`);
      return response.data as Task;
    },
    enabled: !!taskId && !!teamId,
  });
};

export const useCreateTask = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TaskCreateRequest) => {
      const response = await apiClient.post(`/tasks?team_id=${teamId}`, data);
      return response.data as Task;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
    },
  });
};

export const useUpdateTask = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ taskId, data }: { taskId: string; data: TaskUpdateRequest }) => {
      const response = await apiClient.put(`/tasks/${taskId}?team_id=${teamId}`, data);
      return response.data as Task;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
      queryClient.invalidateQueries({ queryKey: ['task', data.id, teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
    },
  });
};

export const useDeleteTask = (teamId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      await apiClient.delete(`/tasks/${taskId}?team_id=${teamId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', teamId] });
      queryClient.invalidateQueries({ queryKey: ['board', teamId] });
    },
  });
};
