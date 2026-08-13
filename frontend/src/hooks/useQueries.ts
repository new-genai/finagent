import { useQuery, useMutation } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { ChatRequest, RetrieveRequest, ExecuteRequest } from '@/types/api';

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiService.getHealth,
    refetchInterval: 30000, // Tự động refetch mỗi 30s để check status
  });
};

export const useDatasetStats = () => {
  return useQuery({
    queryKey: ['datasetStats'],
    queryFn: apiService.getDatasetStats,
  });
};

export const useChatMutation = () => {
  return useMutation({
    mutationFn: (data: ChatRequest) => apiService.chatEndToEnd(data),
  });
};

export const useRetrieveMutation = () => {
  return useMutation({
    mutationFn: (data: RetrieveRequest) => apiService.retrieveTables(data),
  });
};

export const useExecuteMutation = () => {
  return useMutation({
    mutationFn: (data: ExecuteRequest) => apiService.executeCode(data),
  });
};

export const useSubmissionMutation = () => {
  return useMutation({
    mutationFn: apiService.generateSubmission,
  });
};
