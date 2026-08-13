import { apiClient } from '@/lib/api-client';
import { 
  RetrieveRequest, RetrieveResponse, 
  ExecuteRequest, ExecuteResponse, 
  ChatRequest, ChatResponse, 
  DatasetStatsResponse 
} from '@/types/api';

export const apiService = {
  getHealth: () => apiClient.get<{status: string, version: string}>('/health'),
  getDatasetStats: () => apiClient.get<DatasetStatsResponse>('/dataset/statistics'),
  retrieveTables: (data: RetrieveRequest) => apiClient.post<RetrieveResponse>('/retrieve', data),
  executeCode: (data: ExecuteRequest) => apiClient.post<ExecuteResponse>('/execute', data),
  chatEndToEnd: (data: ChatRequest) => apiClient.post<ChatResponse>('/chat', data),
  generateSubmission: () => apiClient.post<{status: string, message: string}>('/submission', {}),
};
