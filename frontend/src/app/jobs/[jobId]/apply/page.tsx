"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { Briefcase, MapPin, Clock, Upload, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const applySchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address"),
  phone: z.string().optional(),
});

type ApplyForm = z.infer<typeof applySchema>;

interface JobDetail {
  id: string;
  title: string;
  description: string | null;
  location: string | null;
  employment_type: string | null;
  created_at: string | null;
}

export default function ApplyPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;

  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ApplyForm>({
    resolver: zodResolver(applySchema),
  });

  useEffect(() => {
    if (!jobId) return;
    fetch(`${API_BASE}/public/jobs/${jobId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Job not found");
        return r.json();
      })
      .then(setJob)
      .catch(() => setError("Job not found"))
      .finally(() => setLoading(false));
  }, [jobId]);

  const onSubmit = async (data: ApplyForm) => {
    if (!file) {
      setError("Please upload your resume");
      return;
    }
    setError("");
    setSubmitting(true);

    const formData = new FormData();
    formData.append("first_name", data.first_name);
    formData.append("last_name", data.last_name);
    formData.append("email", data.email);
    if (data.phone) formData.append("phone", data.phone);
    formData.append("resume", file);

    try {
      const res = await fetch(`${API_BASE}/public/jobs/${jobId}/apply`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Application failed");
      }
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || "Failed to submit application");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
          <p className="text-sm text-zinc-500">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 p-4">
        <Card className="w-full max-w-md text-center">
          <CardContent className="py-12">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
              <CheckCircle className="h-8 w-8 text-emerald-600" />
            </div>
            <CardTitle className="mb-2">Application Submitted!</CardTitle>
            <CardDescription className="mb-6">
              Your application has been received. Our AI will review your resume and the team will be in touch.
            </CardDescription>
            <Link href="/jobs">
              <Button variant="outline">Browse More Jobs</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 p-4">
        <Card className="w-full max-w-md text-center">
          <CardContent className="py-12">
            <AlertCircle className="mx-auto mb-4 h-10 w-10 text-rose-500" />
            <CardTitle className="mb-2">Job Not Found</CardTitle>
            <Link href="/jobs">
              <Button variant="outline">View All Jobs</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center gap-3 px-4 py-6 sm:px-6">
          <Link href="/jobs" className="text-sm text-zinc-500 hover:text-zinc-900">&larr; Back to jobs</Link>
        </div>
      </header>

      <main className="mx-auto grid max-w-4xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-5">
        {/* Job details */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{job.title}</CardTitle>
              <CardDescription className="space-y-2">
                {job.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" /> {job.location}
                  </span>
                )}
                {job.employment_type && (
                  <Badge variant="secondary">{job.employment_type}</Badge>
                )}
                {job.created_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> Posted{" "}
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            {job.description && (
              <CardContent>
                <p className="text-sm text-zinc-600">{job.description}</p>
              </CardContent>
            )}
          </Card>
        </div>

        {/* Application form */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle>Apply for this position</CardTitle>
              <CardDescription>Fill out the form and upload your resume</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
                    <AlertCircle className="h-4 w-4 shrink-0" />
                    {error}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-700">First Name *</label>
                    <input {...register("first_name")} className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900" />
                    {errors.first_name && <p className="text-xs text-rose-500">{errors.first_name.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-700">Last Name *</label>
                    <input {...register("last_name")} className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900" />
                    {errors.last_name && <p className="text-xs text-rose-500">{errors.last_name.message}</p>}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-700">Email *</label>
                  <input type="email" {...register("email")} className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900" placeholder="you@example.com" />
                  {errors.email && <p className="text-xs text-rose-500">{errors.email.message}</p>}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-700">Phone <span className="text-zinc-400">(optional)</span></label>
                  <input {...register("phone")} className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900" placeholder="+1 (555) 123-4567" />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-700">Resume *</label>
                  <label className="flex cursor-pointer items-center justify-center gap-3 rounded-lg border-2 border-dashed border-zinc-300 p-6 text-sm text-zinc-500 hover:border-zinc-900 hover:text-zinc-700">
                    <Upload className="h-5 w-5" />
                    {file ? file.name : "Upload your resume (PDF or DOCX)"}
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      className="hidden"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                  </label>
                </div>

                <Button type="submit" className="w-full bg-zinc-900 text-white hover:bg-zinc-800" disabled={submitting}>
                  {submitting ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Submitting...</>
                  ) : (
                    "Submit Application"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}