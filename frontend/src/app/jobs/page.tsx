"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Briefcase, MapPin, Clock, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const API_BASE = "/api/v1";

interface PublicJob {
  id: string;
  title: string;
  description: string | null;
  location: string | null;
  employment_type: string | null;
  status: string;
  created_at: string | null;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function PublicJobsPage() {
  const [jobs, setJobs] = useState<PublicJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/public/jobs`)
      .then((r) => {
        if (!r.ok) throw new Error("Failed to fetch");
        return r.json();
      })
      .then((data) => {
        setJobs(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load jobs");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
          <p className="text-sm text-zinc-500">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-6 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900">
              <Briefcase className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-zinc-900">AI-ATS Careers</h1>
              <p className="text-sm text-zinc-500">Find your next opportunity</p>
            </div>
          </div>
          <Link href="/login">
            <Button variant="outline" size="sm">Recruiter Login</Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-zinc-900">Open Positions</h2>
          <p className="mt-1 text-zinc-500">{jobs.length} job{jobs.length !== 1 ? "s" : ""} available</p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {jobs.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
                <Briefcase className="h-10 w-10 text-zinc-300" />
                <p className="text-zinc-500">No open positions right now. Check back soon!</p>
              </CardContent>
            </Card>
          ) : (
            jobs.map((job) => (
              <Card key={job.id} className="transition-shadow hover:shadow-md">
                <CardContent className="flex items-center justify-between p-6">
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-zinc-900">{job.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-sm text-zinc-500">
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
                          <Clock className="h-3.5 w-3.5" /> Posted {formatDate(job.created_at)}
                        </span>
                      )}
                    </div>
                  </div>
                  <Link href={`/jobs/${job.id}/apply`}>
                    <Button className="gap-2 bg-zinc-900 text-white hover:bg-zinc-800">
                      Apply <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  );
}