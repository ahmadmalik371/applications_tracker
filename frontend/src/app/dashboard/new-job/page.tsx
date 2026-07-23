"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import apiClient from "@/lib/api-client";
import { AuthGuard } from "@/components/auth-guard";

const jobSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  location: z.string().optional(),
  employment_type: z.string().optional(),
});

type JobForm = z.infer<typeof jobSchema>;

export default function NewJobPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<JobForm>({
    resolver: zodResolver(jobSchema),
  });
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (values: JobForm) => {
    setError(null);
    try {
      await apiClient.post("/jobs", values);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to create job.");
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-zinc-50 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-3xl">
        <Card>
          <CardHeader>
            <CardTitle>Post a New Job</CardTitle>
            <CardDescription>Publish a job posting for your recruiting team.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {error && (
                <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                  {error}
                </div>
              )}
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm">
                  <span>Job Title</span>
                  <input
                    {...register("title")}
                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                  {errors.title && <p className="text-xs text-rose-500">{errors.title.message}</p>}
                </label>
                <label className="space-y-2 text-sm">
                  <span>Location</span>
                  <input
                    {...register("location")}
                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                </label>
              </div>
              <div className="space-y-2 text-sm">
                <label>Employment Type</label>
                <input
                  {...register("employment_type")}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                />
              </div>
              <div className="space-y-2 text-sm">
                <label>Description</label>
                <textarea
                  {...register("description")}
                  rows={6}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                />
              </div>
              <div className="flex items-center gap-3">
                <Button type="submit" className="bg-zinc-900 text-white hover:bg-zinc-800" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Create Job"}
                </Button>
                <Button asChild variant="outline" type="button">
                  <a href="/dashboard">Cancel</a>
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
    </AuthGuard>
  );
}
