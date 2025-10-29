/**
 * Tasks API Service
 */

import { apiClient } from './client';
import { Task } from '../types';

export interface GetTasksParams {
  business_id?: number;
  status?: string;
  limit?: number;
}

/**
 * Get all tasks with optional filters
 */
export const getTasks = async (params?: GetTasksParams): Promise<Task[]> => {
  const response = await apiClient.get<Task[]>('/tasks/', { params });
  return response.data;
};

/**
 * Get single task by ID
 */
export const getTask = async (taskId: number): Promise<Task> => {
  const response = await apiClient.get<Task>(`/tasks/${taskId}`);
  return response.data;
};

/**
 * Create new task
 */
export const createTask = async (taskData: Partial<Task>): Promise<Task> => {
  const response = await apiClient.post<Task>('/tasks/', taskData);
  return response.data;
};

/**
 * Update task
 */
export const updateTask = async (
  taskId: number,
  taskData: Partial<Task>
): Promise<Task> => {
  const response = await apiClient.patch<Task>(`/tasks/${taskId}`, taskData);
  return response.data;
};

/**
 * Complete task
 */
export const completeTask = async (
  taskId: number,
  actualDuration: number
): Promise<Task> => {
  const response = await apiClient.post<Task>(`/tasks/${taskId}/complete`, {
    actual_duration: actualDuration,
  });
  return response.data;
};

/**
 * Delete task
 */
export const deleteTask = async (taskId: number): Promise<void> => {
  await apiClient.delete(`/tasks/${taskId}`);
};
