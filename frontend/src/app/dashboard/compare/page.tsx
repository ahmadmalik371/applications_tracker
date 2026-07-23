"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, GitCompare, CheckCircle2, XCircle, Trophy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";

interface CompareCandidate {
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  match_score: number;
  confidence: number;
  features: Record<string, number>;
  embedding_similarity: number;
  skills: string[];
  experience_years: number;
  education: Array<{ degree?: string }>;
  location: string;
}

interface CompareResponse {
  job_id: string;
  job_title: string;
  candidates: CompareCandidate[];
}

export default function ComparePage() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const { data: jobs } = useQuery({
    queryKey: ["jobs-list"],
    queryFn: async () => {
      const { data } = await apiClient.get<Array<{ id: string; title: string }>>("/candidates/jobs", {
        params: { limit: 100 },
      });
      return data;
    },
  });

  const { data: candidates } = useQuery({
    queryKey: ["candidates-list"],
    queryFn: async () => {
      const { data } = await apiClient.get<
        Array<{ id: string; first_name: string | null; last_name: string | null; email: string }>
      >("/candidates", { params: { limit: 100 } });
      return data;
    },
  });

  const { data: comparison, isLoading } = useQuery<CompareResponse>({
    queryKey: ["compare", selectedIds, jobId],
    queryFn: async () => {
      const { data } = await apiClient.post<CompareResponse>("/rankings/compare", {
        candidate_ids: selectedIds,
        job_id: jobId,
      });
      return data;
    },
    enabled: submitted && selectedIds.length >= 2 && !!jobId,
  });

  const toggleCandidate = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
    setSubmitted(false);
  };

  const topCandidate = comparison?.candidates[0];

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="mb-2 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
            <ArrowLeft className="h-4 w-4" /> Dashboard
          </Link>
          <h1 className="text-xl font-semibold text-zinc-900">Compare Candidates</h1>
          <p className="text-sm text-zinc-500">Side-by-side comparison for a specific job</p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Selection controls */}
        <Card className="mb-6">
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-zinc-700">Select Job</label>
              <select
                value={jobId ?? ""}
                onChange={(e) => {
                  setJobId(e.target.value || null);
                  setSubmitted(false);
                }}
                className="h-10 w-full max-w-md rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200"
              >
                <option value="">Choose a job...</option>
                {jobs?.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-zinc-700">
                Select Candidates ({selectedIds.length} selected)
              </label>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {candidates?.map((c) => {
                  const isSelected = selectedIds.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      onClick={() => toggleCandidate(c.id)}
                      className={`flex items-center gap-2 rounded-lg border p-2 text-left text-sm transition-colors ${
                        isSelected
                          ? "border-zinc-900 bg-zinc-50"
                          : "border-zinc-200 hover:bg-zinc-50"
                      }`}
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-200 text-xs font-semibold text-zinc-700">
                        {`${c.first_name?.[0] ?? ""}${c.last_name?.[0] ?? ""}`.toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-zinc-800">
                          {c.first_name} {c.last_name}
                        </p>
                        <p className="text-xs text-zinc-500">{c.email}</p>
                      </div>
                      {isSelected && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
                    </button>
                  );
                })}
              </div>
            </div>

            <Button
              onClick={() => setSubmitted(true)}
              disabled={selectedIds.length < 2 || !jobId}
              className="gap-2 bg-zinc-900 text-white"
            >
              <GitCompare className="h-4 w-4" /> Compare {selectedIds.length} candidates
            </Button>
          </CardContent>
        </Card>

        {/* Comparison table */}
        {submitted && isLoading && (
          <Skeleton className="h-64 w-full" />
        )}

        {submitted && !isLoading && comparison && (
          <div>
            <div className="mb-4 flex items-center gap-2">
              <Trophy className="h-5 w-5 text-amber-500" />
              <p className="text-sm text-zinc-600">
                Top match: <strong>{topCandidate?.candidate_name}</strong> ({topCandidate?.match_score.toFixed(0)}/100)
              </p>
            </div>

            <Card className="overflow-x-auto">
              <CardContent className="p-0">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-100 bg-zinc-50">
                      <th className="p-3 text-left font-medium text-zinc-500">Attribute</th>
                      {comparison.candidates.map((c) => (
                        <th key={c.candidate_id} className="p-3 text-left">
                          <Link href={`/candidates/${c.candidate_id}`} className="hover:underline">
                            {c.candidate_name}
                          </Link>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <CompareRow label="Match Score" values={comparison.candidates.map((c) => `${c.match_score.toFixed(0)}/100`)} highlight="max" scores={comparison.candidates.map((c) => c.match_score)} />
                    <CompareRow label="Confidence" values={comparison.candidates.map((c) => `${(c.confidence * 100).toFixed(0)}%`)} />
                    <CompareRow label="Experience (years)" values={comparison.candidates.map((c) => String(c.experience_years))} highlight="max" scores={comparison.candidates.map((c) => c.experience_years)} />
                    <CompareRow label="Location" values={comparison.candidates.map((c) => c.location || "—")} />
                    <CompareRow
                      label="Skills"
                      values={comparison.candidates.map((c) => c.skills.join(", ") || "—")}
                      render={(val, i) => (
                        <div className="flex flex-wrap gap-1">
                          {comparison.candidates[i].skills.map((s) => (
                            <Badge key={s} variant="secondary" className="bg-zinc-100 text-xs">{s}</Badge>
                          ))}
                        </div>
                      )}
                    />
                    <CompareRow
                      label="Education"
                      values={comparison.candidates.map((c) => c.education.map((e) => e.degree).join(", ") || "—")}
                    />
                    <CompareRow
                      label="Embedding Similarity"
                      values={comparison.candidates.map((c) => `${(c.embedding_similarity * 100).toFixed(0)}%`)}
                      highlight="max"
                      scores={comparison.candidates.map((c) => c.embedding_similarity)}
                    />
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </div>
        )}

        {submitted && !isLoading && !comparison && (
          <p className="py-8 text-center text-sm text-rose-500">Failed to load comparison</p>
        )}
      </main>
    </div>
  );
}

function CompareRow({
  label,
  values,
  highlight,
  scores,
  render,
}: {
  label: string;
  values: string[];
  highlight?: "max";
  scores?: number[];
  render?: (val: string, i: number) => React.ReactNode;
}) {
  let maxIdx = -1;
  if (highlight === "max" && scores) {
    maxIdx = scores.indexOf(Math.max(...scores));
  }

  return (
    <tr className="border-b border-zinc-50 last:border-0">
      <td className="p-3 font-medium text-zinc-500">{label}</td>
      {values.map((val, i) => (
        <td key={i} className={`p-3 ${i === maxIdx ? "bg-emerald-50 font-semibold text-emerald-700" : "text-zinc-700"}`}>
          {render ? render(val, i) : val}
        </td>
      ))}
    </tr>
  );
}
