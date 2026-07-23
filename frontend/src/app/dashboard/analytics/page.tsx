"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, TrendingUp, Clock, Users, Target, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";

export default function AnalyticsPage() {
  const { data: funnel, isLoading: funnelLoading } = useQuery({
    queryKey: ["analytics", "funnel"],
    queryFn: async () => {
      const { data } = await apiClient.get("/analytics/funnel");
      return data as { stages: Record<string, number>; total: number; conversion_rates: Record<string, number> };
    },
  });

  const { data: tth, isLoading: tthLoading } = useQuery({
    queryKey: ["analytics", "time-to-hire"],
    queryFn: async () => {
      const { data } = await apiClient.get("/analytics/time-to-hire");
      return data as { average_days: number; count: number; min_days: number; max_days: number };
    },
  });

  const { data: sources, isLoading: sourcesLoading } = useQuery({
    queryKey: ["analytics", "sources"],
    queryFn: async () => {
      const { data } = await apiClient.get("/analytics/source-tracking");
      return data as { sources: Record<string, number>; total: number };
    },
  });

  const { data: aiAccuracy, isLoading: aiLoading } = useQuery({
    queryKey: ["analytics", "ai-accuracy"],
    queryFn: async () => {
      const { data } = await apiClient.get("/analytics/ai-accuracy");
      return data as { avg_score_hired: number; avg_score_rejected: number; hired_count: number; rejected_count: number };
    },
  });

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="mb-1 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
            <ArrowLeft className="h-4 w-4" /> Dashboard
          </Link>
          <h1 className="text-xl font-semibold text-zinc-900">Analytics</h1>
          <p className="text-sm text-zinc-500">Hiring funnel, time-to-hire, source tracking, and AI accuracy</p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 flex justify-end">
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="h-4 w-4" /> Export Report
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Funnel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-sky-600" /> Hiring Funnel</CardTitle>
              <CardDescription>Application counts by stage</CardDescription>
            </CardHeader>
            <CardContent>
              {funnelLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : funnel?.stages ? (
                <div className="space-y-3">
                  {Object.entries(funnel.stages).map(([stage, count]) => (
                    <div key={stage}>
                      <div className="flex justify-between text-sm">
                        <span className="font-medium text-zinc-700">{stage}</span>
                        <span className="text-zinc-500">{count} ({funnel.conversion_rates[stage]}%)</span>
                      </div>
                      <Progress value={funnel.conversion_rates[stage]} className="mt-1" />
                    </div>
                  ))}
                  {Object.keys(funnel.stages).length === 0 && (
                    <p className="py-4 text-center text-sm text-zinc-400">No data</p>
                  )}
                </div>
              ) : null}
            </CardContent>
          </Card>

          {/* Time to Hire */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Clock className="h-5 w-5 text-amber-600" /> Time to Hire</CardTitle>
              <CardDescription>Average days from application to hired</CardDescription>
            </CardHeader>
            <CardContent>
              {tthLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  <MetricBox label="Average" value={`${tth?.average_days ?? 0}d`} />
                  <MetricBox label="Count" value={String(tth?.count ?? 0)} />
                  <MetricBox label="Min" value={`${tth?.min_days ?? 0}d`} />
                  <MetricBox label="Max" value={`${tth?.max_days ?? 0}d`} />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Source Tracking */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Users className="h-5 w-5 text-emerald-600" /> Source Tracking</CardTitle>
              <CardDescription>Candidate counts by source</CardDescription>
            </CardHeader>
            <CardContent>
              {sourcesLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : sources?.sources ? (
                <div className="space-y-2">
                  {Object.entries(sources.sources).map(([source, count]) => (
                    <div key={source} className="flex items-center justify-between rounded-lg bg-zinc-50 p-2">
                      <span className="text-sm font-medium text-zinc-700 capitalize">{source}</span>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  ))}
                  {Object.keys(sources.sources).length === 0 && (
                    <p className="py-4 text-center text-sm text-zinc-400">No data</p>
                  )}
                </div>
              ) : null}
            </CardContent>
          </Card>

          {/* AI Accuracy */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-violet-600" /> AI Accuracy</CardTitle>
              <CardDescription>AI scores vs actual outcomes</CardDescription>
            </CardHeader>
            <CardContent>
              {aiLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : (
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-emerald-700">Avg score (hired)</span>
                      <span className="font-semibold">{aiAccuracy?.avg_score_hired ?? 0}</span>
                    </div>
                    <Progress value={aiAccuracy?.avg_score_hired ?? 0} className="mt-1" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-rose-700">Avg score (rejected)</span>
                      <span className="font-semibold">{aiAccuracy?.avg_score_rejected ?? 0}</span>
                    </div>
                    <Progress value={aiAccuracy?.avg_score_rejected ?? 0} className="mt-1" />
                  </div>
                  <div className="flex gap-4 text-sm text-zinc-500">
                    <span>Hired: {aiAccuracy?.hired_count ?? 0}</span>
                    <span>Rejected: {aiAccuracy?.rejected_count ?? 0}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function MetricBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-zinc-100 p-4">
      <p className="text-sm text-zinc-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-zinc-900">{value}</p>
    </div>
  );
}
