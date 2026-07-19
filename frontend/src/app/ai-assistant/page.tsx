"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Sparkles,
  Search,
  FileText,
  Briefcase,
  HelpCircle,
  GitCompare,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";

export default function AIAssistantPage() {
  const [candidateId, setCandidateId] = useState("");
  const [jobId, setJobId] = useState("");
  const [forceRegen, setForceRegen] = useState(false);

  const { data: summary, isLoading: summaryLoading, refetch: refetchSummary } = useQuery({
    queryKey: ["ai-summary", candidateId, forceRegen],
    queryFn: () => apiClient.get(`/ai-assistant/summarize/${candidateId}`, { params: { force: forceRegen } }).then((r) => r.data),
    enabled: !!candidateId,
  });

  const { data: jdAnalysis, isLoading: jdLoading } = useQuery({
    queryKey: ["ai-jd", jobId],
    queryFn: () => apiClient.get(`/ai-assistant/analyze-jd/${jobId}`).then((r) => r.data),
    enabled: !!jobId,
  });

  const { data: skillGap, isLoading: gapLoading } = useQuery({
    queryKey: ["ai-skill-gap", candidateId, jobId],
    queryFn: () => apiClient.get(`/ai-assistant/skill-gap/${candidateId}/${jobId}`).then((r) => r.data),
    enabled: !!candidateId && !!jobId,
  });

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-violet-600" />
            <div>
              <h1 className="text-xl font-semibold tracking-tight text-zinc-900">AI Assistant</h1>
              <p className="text-sm text-zinc-500">Summarization, JD analysis, skill gap, and more</p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">Candidate ID</label>
            <input
              type="text"
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              placeholder="Enter candidate UUID"
              className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm focus:border-zinc-400 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-700">Job ID</label>
            <input
              type="text"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              placeholder="Enter job UUID"
              className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm focus:border-zinc-400 focus:outline-none"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Resume Summary */}
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-sky-600" />
                <div>
                  <CardTitle>Resume Summary</CardTitle>
                  <CardDescription>AI-generated summary</CardDescription>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => { setForceRegen(!forceRegen); refetchSummary(); }}
                disabled={!candidateId}
              >
                <RefreshCw className="mr-1 h-3 w-3" /> Regenerate
              </Button>
            </CardHeader>
            <CardContent>
              {summaryLoading ? (
                <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-full" />)}</div>
              ) : summary?.summary ? (
                <div className="space-y-3">
                  <p className="text-sm text-zinc-700">{summary.summary.professional_summary}</p>
                  {summary.summary.highlights?.length > 0 && (
                    <div>
                      <span className="text-xs font-medium text-zinc-500">Highlights</span>
                      <ul className="mt-1 list-inside list-disc text-sm text-zinc-700">
                        {summary.summary.highlights.map((h: string, i: number) => <li key={i}>{h}</li>)}
                      </ul>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {summary.summary.skills?.map((s: string, i: number) => (
                      <Badge key={i} variant="secondary">{s}</Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="py-4 text-center text-sm text-zinc-400">Enter a candidate ID to generate summary</p>
              )}
            </CardContent>
          </Card>

          {/* JD Analysis */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-amber-600" />
                <div>
                  <CardTitle>JD Analysis</CardTitle>
                  <CardDescription>Job description quality check</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {jdLoading ? (
                <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-full" />)}</div>
              ) : jdAnalysis?.analysis ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-zinc-700">Score</span>
                    <Badge variant={jdAnalysis.analysis.score > 70 ? "success" : "warning"}>
                      {jdAnalysis.analysis.score}/100
                    </Badge>
                  </div>
                  {jdAnalysis.analysis.issues?.length > 0 && (
                    <div>
                      <span className="text-xs font-medium text-zinc-500">Issues</span>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {jdAnalysis.analysis.issues.map((issue: string, i: number) => (
                          <Badge key={i} variant="destructive">{issue.replace(/_/g, " ")}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {jdAnalysis.analysis.suggestions?.length > 0 && (
                    <div>
                      <span className="text-xs font-medium text-zinc-500">Suggestions</span>
                      <ul className="mt-1 list-inside list-disc text-sm text-zinc-700">
                        {jdAnalysis.analysis.suggestions.map((s: string, i: number) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p className="py-4 text-center text-sm text-zinc-400">Enter a job ID to analyze</p>
              )}
            </CardContent>
          </Card>

          {/* Skill Gap */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <GitCompare className="h-5 w-5 text-violet-600" />
                <div>
                  <CardTitle>Skill Gap Analysis</CardTitle>
                  <CardDescription>Candidate vs job requirements</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {gapLoading ? (
                <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-4 w-full" />)}</div>
              ) : skillGap?.analysis ? (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <span className="text-xs font-medium text-emerald-600">Strong Skills</span>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {skillGap.analysis.strong_skills?.map((s: string, i: number) => (
                        <Badge key={i} variant="success">{s}</Badge>
                      ))}
                      {skillGap.analysis.strong_skills?.length === 0 && <span className="text-sm text-zinc-400">None</span>}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-rose-600">Missing Skills</span>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {skillGap.analysis.missing_skills?.map((s: string, i: number) => (
                        <Badge key={i} variant="destructive">{s}</Badge>
                      ))}
                      {skillGap.analysis.missing_skills?.length === 0 && <span className="text-sm text-zinc-400">None</span>}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-zinc-500">Readiness Score</span>
                    <div className="mt-1 text-2xl font-bold text-zinc-900">
                      {skillGap.analysis.readiness_score}%
                    </div>
                  </div>
                </div>
              ) : (
                <p className="py-4 text-center text-sm text-zinc-400">Enter both candidate and job IDs</p>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
