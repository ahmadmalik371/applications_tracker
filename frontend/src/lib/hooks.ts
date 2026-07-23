import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "./api-client";

export interface DashboardStats {
  active_jobs: number;
  total_jobs: number;
  total_candidates: number;
  new_candidates: number;
  total_applications: number;
  pipeline: Record<string, number>;
  recent_jobs: Array<{
    id: string;
    title: string;
    status: string;
    location: string | null;
    created_at: string | null;
  }>;
  recent_candidates: Array<{
    id: string;
    first_name: string | null;
    last_name: string | null;
    email: string;
    status: string;
    created_at: string | null;
  }>;
}

export interface NotificationItem {
  id: string;
  organization_id: string;
  user_id?: string;
  channel: string;
  title: string;
  message: string;
  status: string;
  read: boolean;
  created_at: string | null;
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardStats>("/dashboard/stats");
      return data;
    },
    refetchInterval: 30_000,
  });
}

export function useNotifications(limit = 5) {
  return useQuery<NotificationItem[]>({
    queryKey: ["notifications", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<NotificationItem[]>("/notifications", {
        params: { limit },
      });
      return data;
    },
    refetchInterval: 30_000,
  });
}

export function useUnreadNotificationCount() {
  return useQuery<number>({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ unread: number }>("/notifications/unread-count");
      return data.unread;
    },
    refetchInterval: 30_000,
  });
}

export interface JobSummary {
  id: string;
  title: string;
  status: string;
  location: string | null;
  employment_type: string | null;
  created_at: string | null;
}

export function useJobs(skip = 0, limit = 50) {
  return useQuery<JobSummary[]>({
    queryKey: ["jobs", skip, limit],
    queryFn: async () => {
      const { data } = await apiClient.get<JobSummary[]>("/jobs", {
        params: { skip, limit },
      });
      return data;
    },
  });
}

export interface CandidateSummary {
  id: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  status: string;
  created_at: string | null;
}

export function useCandidates(skip = 0, limit = 50) {
  return useQuery<CandidateSummary[]>({
    queryKey: ["candidates", skip, limit],
    queryFn: async () => {
      const { data } = await apiClient.get<CandidateSummary[]>("/candidates", {
        params: { skip, limit },
      });
      return data;
    },
  });
}

export interface RankedCandidate {
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  match_score: number;
  confidence: number;
  features: Record<string, number>;
  embedding_similarity: number;
  breakdown: Record<string, number>;
}

export function useRankingForJob(jobId: string | null, limit = 10) {
  return useQuery<RankedCandidate[]>({
    queryKey: ["rankings", jobId, limit],
    queryFn: async () => {
      if (!jobId) return [];
      const { data } = await apiClient.get<RankedCandidate[]>(
        `/rankings/candidates/${jobId}`,
        { params: { limit } }
      );
      return data;
    },
    enabled: !!jobId,
  });
}

export interface JobCreateInput {
  title: string;
  description?: string;
  location?: string;
  employment_type?: string;
}

export function useCreateJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: JobCreateInput) => {
      const { data } = await apiClient.post("/candidates/jobs", input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });
}
