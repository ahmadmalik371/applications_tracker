"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Calendar, Video, MapPin, Star, Plus, X } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";

interface Interview {
  id: string;
  application_id: string;
  interview_type: string;
  scheduled_at: string;
  duration_minutes: number;
  location: string | null;
  meeting_link: string | null;
  status: string;
  notes: string | null;
}

interface Feedback {
  id: string;
  interview_id: string;
  panelist_id: string;
  rating: number;
  strengths: string | null;
  weaknesses: string | null;
  recommendation: string | null;
  notes: string | null;
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  phone: <Calendar className="h-4 w-4" />,
  video: <Video className="h-4 w-4" />,
  onsite: <MapPin className="h-4 w-4" />,
  technical: <Star className="h-4 w-4" />,
};

export default function InterviewsPage() {
  const [applicationId, setApplicationId] = useState("");
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: interviews, isLoading } = useQuery<Interview[]>({
    queryKey: ["interviews", applicationId],
    queryFn: async () => {
      if (!applicationId) return [];
      const { data } = await apiClient.get<Interview[]>(`/interviews/application/${applicationId}`);
      return data;
    },
    enabled: !!applicationId,
  });

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <a href="/dashboard" className="mb-1 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700">
            <ArrowLeft className="h-4 w-4" /> Dashboard
          </a>
          <h1 className="text-xl font-semibold text-zinc-900">Interview Management</h1>
          <p className="text-sm text-zinc-500">Schedule and track interviews</p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Card className="mb-6">
          <CardContent>
            <label className="mb-1.5 block text-sm font-medium text-zinc-700">Application ID</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={applicationId}
                onChange={(e) => setApplicationId(e.target.value)}
                placeholder="Enter application UUID..."
                className="h-10 flex-1 rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200"
              />
              <Button onClick={() => setShowForm(true)} disabled={!applicationId} className="gap-2 bg-zinc-900 text-white">
                <Plus className="h-4 w-4" /> Schedule
              </Button>
            </div>
          </CardContent>
        </Card>

        {showForm && <ScheduleForm applicationId={applicationId} onClose={() => setShowForm(false)} />}

        {isLoading && <Skeleton className="h-40 w-full" />}

        {!isLoading && interviews && interviews.length === 0 && applicationId && (
          <p className="py-8 text-center text-sm text-zinc-400">No interviews scheduled</p>
        )}

        {interviews && interviews.length > 0 && (
          <div className="space-y-4">
            {interviews.map((iv) => (
              <InterviewCard key={iv.id} interview={iv} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function ScheduleForm({ applicationId, onClose }: { applicationId: string; onClose: () => void }) {
  const qc = useQueryClient();
  const [type, setType] = useState("phone");
  const [scheduledAt, setScheduledAt] = useState("");
  const [duration, setDuration] = useState(60);
  const [location, setLocation] = useState("");
  const [link, setLink] = useState("");

  const create = useMutation({
    mutationFn: async () => {
      await apiClient.post("/interviews", {
        application_id: applicationId,
        interview_type: type,
        scheduled_at: scheduledAt,
        duration_minutes: duration,
        location: location || null,
        meeting_link: link || null,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["interviews", applicationId] });
      onClose();
    },
  });

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Schedule Interview</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="h-4 w-4" /></Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-600">Type</label>
            <select value={type} onChange={(e) => setType(e.target.value)} className="h-9 w-full rounded-md border border-zinc-200 px-2 text-sm">
              <option value="phone">Phone</option>
              <option value="video">Video</option>
              <option value="onsite">On-site</option>
              <option value="technical">Technical</option>
              <option value="cultural">Cultural</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-600">When</label>
            <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} className="h-9 w-full rounded-md border border-zinc-200 px-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-600">Duration (min)</label>
            <input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="h-9 w-full rounded-md border border-zinc-200 px-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-zinc-600">Location</label>
            <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} className="h-9 w-full rounded-md border border-zinc-200 px-2 text-sm" />
          </div>
        </div>
        <Button onClick={() => create.mutate()} disabled={create.isPending || !scheduledAt} className="bg-zinc-900 text-white">
          {create.isPending ? "Scheduling..." : "Schedule Interview"}
        </Button>
      </CardContent>
    </Card>
  );
}

function InterviewCard({ interview }: { interview: Interview }) {
  const [showFeedback, setShowFeedback] = useState(false);
  const qc = useQueryClient();

  const { data: feedback } = useQuery<Feedback[]>({
    queryKey: ["feedback", interview.id],
    queryFn: async () => {
      const { data } = await apiClient.get<Feedback[]>(`/interviews/${interview.id}/feedback`);
      return data;
    },
  });

  const statusUpdate = useMutation({
    mutationFn: async (status: string) => {
      await apiClient.patch(`/interviews/${interview.id}/status`, { status });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["interviews", interview.application_id] });
    },
  });

  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-100">
            {TYPE_ICONS[interview.interview_type] ?? <Calendar className="h-4 w-4" />}
          </div>
          <div>
            <p className="font-medium text-zinc-900 capitalize">{interview.interview_type} Interview</p>
            <p className="text-sm text-zinc-500">
              {new Date(interview.scheduled_at).toLocaleString()} · {interview.duration_minutes} min
            </p>
            {interview.location && <p className="text-xs text-zinc-400">{interview.location}</p>}
            {interview.meeting_link && (
              <a href={interview.meeting_link} target="_blank" rel="noopener" className="text-xs text-sky-600 hover:underline">
                Join meeting
              </a>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={interview.status === "Completed" ? "success" : interview.status === "Cancelled" ? "destructive" : "default"}>
            {interview.status}
          </Badge>
          <div className="flex gap-1">
            <Button size="sm" variant="outline" onClick={() => statusUpdate.mutate("Completed")}>Complete</Button>
            <Button size="sm" variant="outline" onClick={() => setShowFeedback(true)}>Feedback</Button>
          </div>
        </div>
      </CardContent>
      {showFeedback && (
        <FeedbackSection interviewId={interview.id} feedback={feedback ?? []} onClose={() => setShowFeedback(false)} />
      )}
    </Card>
  );
}

function FeedbackSection({ interviewId, feedback, onClose }: { interviewId: string; feedback: Feedback[]; onClose: () => void }) {
  const qc = useQueryClient();
  const [rating, setRating] = useState(5);
  const [strengths, setStrengths] = useState("");
  const [weaknesses, setWeaknesses] = useState("");
  const [recommendation, setRecommendation] = useState("");

  const submit = useMutation({
    mutationFn: async () => {
      await apiClient.post(`/interviews/${interviewId}/feedback`, {
        rating,
        strengths: strengths || null,
        weaknesses: weaknesses || null,
        recommendation: recommendation || null,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["feedback", interviewId] });
      setStrengths("");
      setWeaknesses("");
    },
  });

  return (
    <div className="border-t border-zinc-100 p-4">
      <h4 className="mb-3 text-sm font-semibold text-zinc-700">Feedback</h4>
      {feedback.length > 0 && (
        <div className="mb-4 space-y-2">
          {feedback.map((f) => (
            <div key={f.id} className="rounded-lg bg-zinc-50 p-2 text-sm">
              <div className="flex items-center gap-2">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} className={cn("h-3.5 w-3.5", i <= f.rating ? "fill-amber-400 text-amber-400" : "text-zinc-300")} />
                  ))}
                </div>
                {f.recommendation && <Badge variant="secondary" className="text-xs">{f.recommendation}</Badge>}
              </div>
              {f.strengths && <p className="mt-1 text-emerald-700">+ {f.strengths}</p>}
              {f.weaknesses && <p className="text-rose-600">- {f.weaknesses}</p>}
            </div>
          ))}
        </div>
      )}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-600">Rating:</span>
          {[1, 2, 3, 4, 5].map((i) => (
            <button key={i} onClick={() => setRating(i)}>
              <Star className={cn("h-5 w-5", i <= rating ? "fill-amber-400 text-amber-400" : "text-zinc-300")} />
            </button>
          ))}
        </div>
        <input type="text" value={strengths} onChange={(e) => setStrengths(e.target.value)} placeholder="Strengths..." className="h-9 w-full rounded-md border border-zinc-200 px-3 text-sm" />
        <input type="text" value={weaknesses} onChange={(e) => setWeaknesses(e.target.value)} placeholder="Weaknesses..." className="h-9 w-full rounded-md border border-zinc-200 px-3 text-sm" />
        <select value={recommendation} onChange={(e) => setRecommendation(e.target.value)} className="h-9 w-full rounded-md border border-zinc-200 px-2 text-sm">
          <option value="">Recommendation...</option>
          <option value="hire">Hire</option>
          <option value="no-hire">No-hire</option>
          <option value="maybe">Maybe</option>
        </select>
        <Button size="sm" onClick={() => submit.mutate()} disabled={submit.isPending} className="bg-zinc-900 text-white">
          Submit Feedback
        </Button>
      </div>
    </div>
  );
}
