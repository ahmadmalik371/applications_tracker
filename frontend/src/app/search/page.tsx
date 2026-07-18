"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Search, ArrowLeft, Sparkles, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";

interface SearchResult {
  candidate_id: string;
  candidate_name: string;
  email: string;
  status: string;
  keyword_score: number;
  semantic_score: number;
  combined_score: number;
  skills: string[];
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["search", submitted],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: SearchResult[]; count: number }>(
        "/candidates/search/hybrid",
        { params: { q: submitted, limit: 20 } }
      );
      return data;
    },
    enabled: submitted.length > 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(query);
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/dashboard" className="mb-2 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
            <ArrowLeft className="h-4 w-4" /> Dashboard
          </Link>
          <h1 className="text-xl font-semibold text-zinc-900">Candidate Search</h1>
          <p className="text-sm text-zinc-500">Hybrid keyword + semantic search</p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Search bar */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by skill, name, experience, or job description..."
              className="h-12 w-full rounded-xl border border-zinc-200 bg-white pl-12 pr-28 text-base shadow-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200"
            />
            <Button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 gap-2 bg-zinc-900 text-white"
              disabled={!query.trim() || isFetching}
            >
              <Sparkles className="h-4 w-4" />
              {isFetching ? "Searching..." : "Search"}
            </Button>
          </div>
        </form>

        {/* Results */}
        {!submitted && (
          <div className="flex flex-col items-center gap-3 py-20 text-center">
            <Search className="h-12 w-12 text-zinc-300" />
            <p className="text-sm text-zinc-400">Start typing to search candidates</p>
          </div>
        )}

        {submitted && isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        )}

        {submitted && !isLoading && data && data.results.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-20 text-center">
            <FileText className="h-12 w-12 text-zinc-300" />
            <p className="text-sm text-zinc-400">No candidates found for "{submitted}"</p>
          </div>
        )}

        {data && data.results.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm text-zinc-500">
              {data.count} candidate{data.count !== 1 ? "s" : ""} found
            </p>
            {data.results.map((result) => (
              <Card key={result.candidate_id} className="transition-shadow hover:shadow-md">
                <CardContent className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 text-xs font-semibold text-white">
                      {result.candidate_name.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <Link
                        href={`/candidates/${result.candidate_id}`}
                        className="font-medium text-zinc-900 hover:underline"
                      >
                        {result.candidate_name}
                      </Link>
                      <p className="text-xs text-zinc-500">{result.email}</p>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {result.skills.map((s) => (
                          <Badge key={s} variant="secondary" className="bg-zinc-100 text-xs">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <div className="flex items-center gap-3 text-xs">
                      <ScoreLabel label="Keyword" value={result.keyword_score} color="text-sky-600" />
                      <ScoreLabel label="Semantic" value={result.semantic_score} color="text-violet-600" />
                      <ScoreLabel label="Combined" value={result.combined_score} color="text-emerald-600" />
                    </div>
                    <div className="w-32">
                      <Progress value={result.combined_score * 100} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function ScoreLabel({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-zinc-400">{label}</span>
      <span className={cn("font-semibold", color)}>{(value * 100).toFixed(0)}%</span>
    </div>
  );
}
