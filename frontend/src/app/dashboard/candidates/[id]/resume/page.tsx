"use client";

import { useParams } from "next/navigation";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  FileText,
  Download,
  Search,
  Highlighter,
  Sparkles,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";

export default function ResumeViewerPage() {
  const params = useParams<{ id: string }>();
  const candidateId = params.id;
  const [keyword, setKeyword] = useState("");

  const { data: candidate, isLoading } = useQuery({
    queryKey: ["candidate-resume", candidateId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/candidates/${candidateId}`);
      return data as {
        id: string;
        first_name: string | null;
        last_name: string | null;
        email: string;
        resume_url: string | null;
        parsed_data: {
          skills?: string[];
          experience?: Array<{ title?: string; company?: string; duration?: string }>;
          education?: Array<{ degree?: string }>;
          location?: string;
        } | null;
        created_at: string | null;
      };
    },
  });

  const parsed = candidate?.parsed_data;
  const allKeywords = useMemo(() => {
    const skills = parsed?.skills ?? [];
    return skills;
  }, [parsed]);

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <Button variant="ghost" size="sm" className="gap-1 text-zinc-500">
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>
          <h1 className="text-lg font-semibold text-zinc-900">Resume Viewer</h1>
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="h-4 w-4" /> Download
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* PDF Viewer */}
          <div className="lg:col-span-2">
            <Card className="overflow-hidden">
              <CardHeader className="border-b border-zinc-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-rose-500" />
                    <div>
                      <CardTitle className="text-base">
                        {isLoading ? (
                          <Skeleton className="h-5 w-40" />
                        ) : (
                          `${candidate?.first_name ?? ""} ${candidate?.last_name ?? ""}`.trim() + " — Resume"
                        )}
                      </CardTitle>
                      <CardDescription className="text-xs">
                        {candidate?.resume_url ? "PDF preview" : "No resume file"}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                      <input
                        type="text"
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        placeholder="Highlight keyword..."
                        className="h-8 w-44 rounded-md border border-zinc-200 pl-8 pr-2 text-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200"
                      />
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {candidate?.resume_url ? (
                  <iframe
                    src={candidate.resume_url}
                    title="Resume PDF"
                    className="h-[70vh] w-full border-0"
                  />
                ) : (
                  <div className="flex h-[70vh] flex-col items-center justify-center gap-3 text-center">
                    <FileText className="h-12 w-12 text-zinc-300" />
                    <p className="text-sm text-zinc-400">No resume uploaded</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar: metadata + AI */}
          <div className="space-y-6">
            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Metadata</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {isLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : (
                  <>
                    <MetaRow label="Name" value={`${candidate?.first_name ?? ""} ${candidate?.last_name ?? ""}`.trim()} />
                    <MetaRow label="Email" value={candidate?.email ?? ""} />
                    <MetaRow label="Location" value={parsed?.location ?? "—"} />
                    <MetaRow label="Skills count" value={String(parsed?.skills?.length ?? 0)} />
                    <MetaRow label="Experience entries" value={String(parsed?.experience?.length ?? 0)} />
                    {candidate?.created_at && (
                      <MetaRow label="Added" value={new Date(candidate.created_at).toLocaleDateString()} />
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Keyword highlighting */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Highlighter className="h-4 w-4 text-amber-500" /> Keywords
                </CardTitle>
                <CardDescription>Click to highlight in the resume</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {allKeywords.length === 0 ? (
                    <p className="text-sm text-zinc-400">No keywords extracted</p>
                  ) : (
                    allKeywords.map((kw) => (
                      <button
                        key={kw}
                        onClick={() => setKeyword(kw)}
                        className="rounded-full border border-zinc-200 px-2.5 py-1 text-xs font-medium text-zinc-600 transition-colors hover:bg-amber-50 hover:text-amber-700"
                      >
                        {kw}
                      </button>
                    ))
                  )}
                </div>
                {keyword && (
                  <div className="mt-3 rounded-lg bg-amber-50 p-2 text-xs text-amber-800">
                    Highlighting: <strong>{keyword}</strong>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AI Sidebar */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-violet-600" /> AI Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {isLoading ? (
                  <Skeleton className="h-24 w-full" />
                ) : (
                  <>
                    <div>
                      <p className="mb-1 font-medium text-zinc-700">Top Skills</p>
                      <div className="flex flex-wrap gap-1.5">
                        {(parsed?.skills ?? []).slice(0, 5).map((s) => (
                          <Badge key={s} variant="secondary" className="bg-violet-100 text-violet-700">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="mb-1 font-medium text-zinc-700">Experience</p>
                      <p className="text-zinc-600">
                        {(parsed?.experience ?? []).length} roles detected
                      </p>
                    </div>
                    <div>
                      <p className="mb-1 font-medium text-zinc-700">Education</p>
                      <p className="text-zinc-600">
                        {(parsed?.education ?? []).length} entries
                      </p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-zinc-500">{label}</span>
      <span className="font-medium text-zinc-800">{value}</span>
    </div>
  );
}
