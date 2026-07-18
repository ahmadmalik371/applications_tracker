"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "./api-client";

export interface CandidateDetail {
  id: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  phone: string | null;
  resume_url: string | null;
  parsed_data: {
    skills?: string[];
    experience?: Array<{ title?: string; company?: string; duration?: string }>;
    education?: Array<{ degree?: string; institution?: string }>;
    location?: string;
  } | null;
  status: string;
  organization_id: string;
  created_at: string | null;
  updated_at: string | null;
}

export function useCandidate(id: string | null) {
  return useQuery<CandidateDetail>({
    queryKey: ["candidate", id],
    queryFn: async () => {
      if (!id) throw new Error("No id");
      const { data } = await apiClient.get<CandidateDetail>(`/candidates/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export interface Tag {
  id: string;
  name: string;
  description: string | null;
  color: string;
  is_active: boolean;
}

export function useTags() {
  return useQuery<Tag[]>({
    queryKey: ["tags"],
    queryFn: async () => {
      const { data } = await apiClient.get<Tag[]>("/recruiter/tags");
      return data;
    },
  });
}

export interface Note {
  id: string;
  candidate_id: string;
  author_id: string;
  content: string;
  is_private: boolean;
  mentions: string[] | null;
  attachments: string[] | null;
  created_at: string;
  updated_at: string;
}

export function useCandidateNotes(candidateId: string | null) {
  return useQuery<Note[]>({
    queryKey: ["notes", candidateId],
    queryFn: async () => {
      if (!candidateId) return [];
      const { data } = await apiClient.get<Note[]>(
        `/recruiter/candidates/${candidateId}/notes`
      );
      return data;
    },
    enabled: !!candidateId,
  });
}

export function useCreateNote(candidateId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { content: string; is_private: boolean }) => {
      const { data } = await apiClient.post<Note>(
        `/recruiter/candidates/${candidateId}/notes`,
        input
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes", candidateId] });
    },
  });
}

export function useUpdateCandidate(id: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: Partial<Pick<CandidateDetail, "status">>) => {
      const { data } = await apiClient.put<CandidateDetail>(
        `/candidates/${id}`,
        input
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["candidate", id] });
    },
  });
}

export interface Explanation {
  summary: string;
  match_score: number;
  confidence: number;
  strengths: string[];
  weaknesses: string[];
  skill_analysis: { matched: string[]; missing: string[]; bonus: string[] };
  recommendations: string[];
  next_steps: string[];
}

export function useExplanation(candidateId: string | null, jobId: string | null) {
  return useQuery<Explanation>({
    queryKey: ["explanation", candidateId, jobId],
    queryFn: async () => {
      if (!candidateId || !jobId) throw new Error("missing ids");
      const { data } = await apiClient.get<Explanation>(
        `/rankings/explain/candidate/${candidateId}/job/${jobId}`
      );
      return data;
    },
    enabled: !!candidateId && !!jobId,
  });
}

export function useJobsList() {
  return useQuery<Array<{ id: string; title: string; status: string }>>({
    queryKey: ["jobs-list"],
    queryFn: async () => {
      const { data } = await apiClient.get("/candidates/jobs", {
        params: { limit: 100 },
      });
      return data;
    },
  });
}
