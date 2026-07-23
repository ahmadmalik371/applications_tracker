"use client";

import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, GripVertical, MoreHorizontal, Filter, CheckSquare, Square } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";

const DEFAULT_STAGES = [
  { key: "Applied", label: "Applied", color: "bg-sky-500" },
  { key: "Screening", label: "Screening", color: "bg-indigo-500" },
  { key: "Interview", label: "Interview", color: "bg-violet-500" },
  { key: "Offer", label: "Offer", color: "bg-amber-500" },
  { key: "Hired", label: "Hired", color: "bg-emerald-500" },
];

interface ApplicationItem {
  id: string;
  candidate_id: string;
  job_id: string;
  status: string;
  score: number | null;
  candidate?: { first_name: string | null; last_name: string | null; email: string };
  job?: { title: string };
}

export default function KanbanPage() {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [dragId, setDragId] = useState<string | null>(null);
  const qc = useQueryClient();

  const { data: jobs } = useQuery({
    queryKey: ["jobs-list"],
    queryFn: async () => {
      const { data } = await apiClient.get<Array<{ id: string; title: string }>>("/candidates/jobs", {
        params: { limit: 100 },
      });
      return data;
    },
  });

  const { data: applications, isLoading } = useQuery<ApplicationItem[]>({
    queryKey: ["applications", selectedJobId],
    queryFn: async () => {
      const params: Record<string, unknown> = { limit: 200 };
      if (selectedJobId) params.job_id = selectedJobId;
      const { data } = await apiClient.get<ApplicationItem[]>("/candidates/applications", { params });
      return data;
    },
  });

  const transition = useMutation({
    mutationFn: async ({ appId, stage }: { appId: string; stage: string }) => {
      await apiClient.post(`/workflow/applications/${appId}/transition`, { to_stage: stage });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications", selectedJobId] });
    },
  });

  const grouped = useMemo(() => {
    const map: Record<string, ApplicationItem[]> = {};
    for (const stage of DEFAULT_STAGES) map[stage.key] = [];
    for (const app of applications ?? []) {
      if (map[app.status]) map[app.status].push(app);
    }
    return map;
  }, [applications]);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const bulkMove = (stage: string) => {
    selectedIds.forEach((id) => transition.mutate({ appId: id, stage }));
    setSelectedIds(new Set());
  };

  const handleDrop = (stage: string) => {
    if (dragId) {
      transition.mutate({ appId: dragId, stage });
      setDragId(null);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/dashboard" className="mb-1 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
                <ArrowLeft className="h-4 w-4" /> Dashboard
              </Link>
              <h1 className="text-xl font-semibold text-zinc-900">Kanban Board</h1>
            </div>
            <div className="flex items-center gap-3">
              <select
                value={selectedJobId ?? ""}
                onChange={(e) => setSelectedJobId(e.target.value || null)}
                className="h-9 rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400"
              >
                <option value="">All jobs</option>
                {jobs?.map((j) => (
                  <option key={j.id} value={j.id}>{j.title}</option>
                ))}
              </select>
              {selectedIds.size > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-zinc-600">{selectedIds.size} selected</span>
                  <Button size="sm" variant="outline" onClick={() => bulkMove("Interview")}>
                    Bulk → Interview
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => bulkMove("Rejected")}>
                    Bulk Reject
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {DEFAULT_STAGES.map((s) => (
              <Skeleton key={s.key} className="h-64 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {DEFAULT_STAGES.map((stage) => (
              <div
                key={stage.key}
                className="flex flex-col rounded-xl border border-zinc-200 bg-zinc-100/50"
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => handleDrop(stage.key)}
              >
                <div className="flex items-center justify-between border-b border-zinc-200 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className={cn("h-2.5 w-2.5 rounded-full", stage.color)} />
                    <span className="text-sm font-semibold text-zinc-700">{stage.label}</span>
                  </div>
                  <Badge variant="secondary" className="bg-zinc-200 text-xs">
                    {grouped[stage.key]?.length ?? 0}
                  </Badge>
                </div>
                <div className="flex-1 space-y-2 p-2">
                  {(grouped[stage.key] ?? []).map((app) => (
                    <div
                      key={app.id}
                      draggable
                      onDragStart={() => setDragId(app.id)}
                      className={cn(
                        "group cursor-move rounded-lg border border-zinc-200 bg-white p-3 shadow-sm transition-all hover:shadow-md",
                        selectedIds.has(app.id) && "ring-2 ring-zinc-900"
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <button onClick={() => toggleSelect(app.id)} className="mt-0.5">
                          {selectedIds.has(app.id) ? (
                            <CheckSquare className="h-4 w-4 text-zinc-900" />
                          ) : (
                            <Square className="h-4 w-4 text-zinc-300" />
                          )}
                        </button>
                        <GripVertical className="h-4 w-4 text-zinc-300 opacity-0 group-hover:opacity-100" />
                      </div>
                      <Link
                        href={`/candidates/${app.candidate_id}`}
                        className="mt-1 block text-sm font-medium text-zinc-900 hover:underline"
                      >
                        {app.candidate?.first_name ?? ""} {app.candidate?.last_name ?? ""}
                      </Link>
                      {app.job?.title && (
                        <p className="text-xs text-zinc-500">{app.job.title}</p>
                      )}
                      {app.score !== null && (
                        <Badge variant="secondary" className="mt-2 bg-violet-100 text-violet-700 text-xs">
                          Score: {app.score.toFixed(0)}
                        </Badge>
                      )}
                    </div>
                  ))}
                  {(grouped[stage.key]?.length ?? 0) === 0 && (
                    <p className="py-4 text-center text-xs text-zinc-400">Drop here</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
