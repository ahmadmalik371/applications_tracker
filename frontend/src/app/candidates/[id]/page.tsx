"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Star,
  XCircle,
  CheckCircle2,
  StickyNote,
  Tag as TagIcon,
  FileText,
  Sparkles,
  Clock,
  Briefcase,
  GraduationCap,
  Plus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import {
  useCandidate,
  useCandidateNotes,
  useCreateNote,
  useUpdateCandidate,
  useExplanation,
  useJobsList,
  useTags,
} from "@/lib/candidate-hooks";
import { cn } from "@/lib/utils";

export default function CandidateDetailPage() {
  const params = useParams<{ id: string }>();
  const candidateId = params.id;

  const { data: candidate, isLoading } = useCandidate(candidateId);
  const { data: jobs } = useJobsList();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const { data: explanation, isLoading: explLoading } = useExplanation(
    candidateId,
    selectedJobId
  );

  const update = useUpdateCandidate(candidateId);

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Button variant="ghost" size="sm" className="mb-2 gap-1 text-zinc-500">
            <ArrowLeft className="h-4 w-4" /> Back to dashboard
          </Button>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 text-lg font-semibold text-white">
                {`${candidate?.first_name?.[0] ?? ""}${candidate?.last_name?.[0] ?? ""}`.toUpperCase()}
              </div>
              <div>
                <h1 className="text-xl font-semibold text-zinc-900">
                  {isLoading ? (
                    <Skeleton className="h-6 w-48" />
                  ) : (
                    `${candidate?.first_name ?? ""} ${candidate?.last_name ?? ""}`.trim()
                  )}
                </h1>
                <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-zinc-500">
                  {candidate?.email && (
                    <span className="flex items-center gap-1">
                      <Mail className="h-3.5 w-3.5" /> {candidate.email}
                    </span>
                  )}
                  {candidate?.phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="h-3.5 w-3.5" /> {candidate.phone}
                    </span>
                  )}
                  {candidate?.parsed_data?.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3.5 w-3.5" /> {candidate.parsed_data.location}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => update.mutate({ status: "Review" })}
                disabled={update.isPending}
              >
                <Star className="h-4 w-4" /> Shortlist
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 text-rose-600 hover:bg-rose-50"
                onClick={() => update.mutate({ status: "Rejected" })}
                disabled={update.isPending}
              >
                <XCircle className="h-4 w-4" /> Reject
              </Button>
              <Button
                size="sm"
                className="gap-2 bg-emerald-600 text-white hover:bg-emerald-700"
                onClick={() => update.mutate({ status: "Interview" })}
                disabled={update.isPending}
              >
                <CheckCircle2 className="h-4 w-4" /> Advance
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Left column: resume + skills + experience */}
          <div className="space-y-6 lg:col-span-2">
            {/* AI Score / Explanation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-violet-600" /> AI Match Analysis
                </CardTitle>
                <CardDescription>Select a job to see AI-powered match analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex flex-wrap gap-2">
                  {jobs?.map((job) => (
                    <button
                      key={job.id}
                      onClick={() => setSelectedJobId(job.id)}
                      className={cn(
                        "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                        selectedJobId === job.id
                          ? "border-zinc-900 bg-zinc-900 text-white"
                          : "border-zinc-200 text-zinc-600 hover:bg-zinc-50"
                      )}
                    >
                      {job.title}
                    </button>
                  ))}
                  {jobs?.length === 0 && (
                    <span className="text-sm text-zinc-400">No jobs available</span>
                  )}
                </div>

                {!selectedJobId ? (
                  <p className="py-8 text-center text-sm text-zinc-400">
                    Select a job to view AI analysis
                  </p>
                ) : explLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                ) : explanation ? (
                  <ExplanationPanel explanation={explanation} />
                ) : (
                  <p className="py-8 text-center text-sm text-rose-500">
                    Failed to load analysis
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Skills */}
            <Card>
              <CardHeader>
                <CardTitle>Skills</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex flex-wrap gap-2">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-7 w-20" />
                    ))}
                  </div>
                ) : candidate?.parsed_data?.skills?.length ? (
                  <div className="flex flex-wrap gap-2">
                    {candidate.parsed_data.skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="bg-zinc-100">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-zinc-400">No skills parsed</p>
                )}
              </CardContent>
            </Card>

            {/* Experience */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5 text-zinc-500" /> Experience
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-3">
                    {[1, 2].map((i) => (
                      <Skeleton key={i} className="h-16 w-full" />
                    ))}
                  </div>
                ) : candidate?.parsed_data?.experience?.length ? (
                  <Timeline
                    items={candidate.parsed_data.experience.map((e) => ({
                      title: e.title ?? "Role",
                      subtitle: e.company ?? "",
                      meta: e.duration ?? "",
                    }))}
                  />
                ) : (
                  <p className="text-sm text-zinc-400">No experience data</p>
                )}
              </CardContent>
            </Card>

            {/* Education */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GraduationCap className="h-5 w-5 text-zinc-500" /> Education
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-16 w-full" />
                ) : candidate?.parsed_data?.education?.length ? (
                  <div className="space-y-3">
                    {candidate.parsed_data.education.map((e, i) => (
                      <div key={i} className="rounded-lg border border-zinc-100 p-3">
                        <p className="font-medium text-zinc-900">{e.degree ?? "Degree"}</p>
                        {e.institution && (
                          <p className="text-sm text-zinc-500">{e.institution}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-zinc-400">No education data</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right column: tags + notes + resume */}
          <div className="space-y-6">
            {/* Tags */}
            <TagsWidget candidateId={candidateId} />

            {/* Notes */}
            <NotesWidget candidateId={candidateId} />

            {/* Resume */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-zinc-500" /> Resume
                </CardTitle>
              </CardHeader>
              <CardContent>
                {candidate?.resume_url ? (
                  <a
                    href={candidate.resume_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 rounded-lg border border-zinc-200 p-3 text-sm text-zinc-700 transition-colors hover:bg-zinc-50"
                  >
                    <FileText className="h-5 w-5 text-rose-500" />
                    View resume
                  </a>
                ) : (
                  <p className="text-sm text-zinc-400">No resume uploaded</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

function ExplanationPanel({ explanation }: { explanation: import("@/lib/candidate-hooks").Explanation }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-medium text-zinc-600">Match Score</span>
            <span className="text-2xl font-bold text-zinc-900">
              {explanation.match_score.toFixed(0)}
              <span className="text-sm text-zinc-400">/100</span>
            </span>
          </div>
          <Progress value={explanation.match_score} className="mt-2" />
        </div>
        <div className="text-right">
          <span className="text-sm font-medium text-zinc-600">Confidence</span>
          <p className="text-lg font-semibold text-violet-600">
            {(explanation.confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <p className="rounded-lg bg-violet-50 p-3 text-sm text-violet-900">
        {explanation.summary}
      </p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <h4 className="mb-2 text-sm font-semibold text-emerald-700">Strengths</h4>
          <ul className="space-y-1">
            {explanation.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-700">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="mb-2 text-sm font-semibold text-rose-700">Weaknesses</h4>
          <ul className="space-y-1">
            {explanation.weaknesses.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-700">
                <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" />
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-semibold text-zinc-700">Skill Analysis</h4>
        <div className="flex flex-wrap gap-2">
          {explanation.skill_analysis.matched.map((s) => (
            <Badge key={s} variant="success">{s}</Badge>
          ))}
          {explanation.skill_analysis.missing.map((s) => (
            <Badge key={s} variant="destructive">{s}</Badge>
          ))}
          {explanation.skill_analysis.bonus.map((s) => (
            <Badge key={s} variant="secondary" className="bg-violet-100 text-violet-700">{s}</Badge>
          ))}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-semibold text-zinc-700">Recommendations</h4>
        <ul className="space-y-1">
          {explanation.recommendations.map((r, i) => (
            <li key={i} className="text-sm text-zinc-600">• {r}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function TagsWidget({ candidateId }: { candidateId: string }) {
  const { data: tags } = useTags();
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TagIcon className="h-5 w-5 text-zinc-500" /> Tags
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {tags?.map((tag) => (
            <Badge key={tag.id} variant="secondary" className="bg-zinc-100">
              {tag.name}
            </Badge>
          ))}
          {tags?.length === 0 && (
            <p className="text-sm text-zinc-400">No tags yet</p>
          )}
        </div>
        <Button variant="outline" size="sm" className="mt-3 gap-1 text-xs">
          <Plus className="h-3 w-3" /> Add tag
        </Button>
      </CardContent>
    </Card>
  );
}

function NotesWidget({ candidateId }: { candidateId: string }) {
  const { data: notes, isLoading } = useCandidateNotes(candidateId);
  const create = useCreateNote(candidateId);
  const [content, setContent] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);

  const handleAdd = () => {
    if (!content.trim()) return;
    create.mutate({ content, is_private: isPrivate });
    setContent("");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <StickyNote className="h-5 w-5 text-zinc-500" /> Notes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 space-y-2">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Add a note..."
            className="w-full rounded-lg border border-zinc-200 p-3 text-sm text-zinc-900 outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200"
            rows={3}
          />
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-xs text-zinc-600">
              <input
                type="checkbox"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
                className="rounded"
              />
              Private
            </label>
            <Button size="sm" onClick={handleAdd} disabled={create.isPending || !content.trim()}>
              Add note
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : notes?.length ? (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="rounded-lg border border-zinc-100 p-3">
                <div className="flex items-start justify-between">
                  <p className="text-sm text-zinc-700">{note.content}</p>
                  {note.is_private && (
                    <Badge variant="secondary" className="ml-2 text-xs">Private</Badge>
                  )}
                </div>
                <p className="mt-2 flex items-center gap-1 text-xs text-zinc-400">
                  <Clock className="h-3 w-3" />
                  {new Date(note.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-400">No notes yet</p>
        )}
      </CardContent>
    </Card>
  );
}

function Timeline({
  items,
}: {
  items: Array<{ title: string; subtitle: string; meta: string }>;
}) {
  return (
    <div className="relative space-y-4 pl-6">
      <div className="absolute left-2 top-2 bottom-2 w-px bg-zinc-200" />
      {items.map((item, i) => (
        <div key={i} className="relative">
          <div className="absolute -left-[18px] top-1.5 h-3 w-3 rounded-full border-2 border-white bg-zinc-400" />
          <p className="font-medium text-zinc-900">{item.title}</p>
          {item.subtitle && <p className="text-sm text-zinc-600">{item.subtitle}</p>}
          {item.meta && <p className="text-xs text-zinc-400">{item.meta}</p>}
        </div>
      ))}
    </div>
  );
}
