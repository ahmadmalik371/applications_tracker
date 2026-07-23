"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Briefcase, MapPin, Clock, ArrowRight, MoreHorizontal, FileText, BarChart2, Edit, Trash2, Copy, Archive, CalendarDays, DollarSign, Building } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AuthGuard } from "@/components/auth-guard";
import apiClient from "@/lib/api-client";

interface Job {
  id: string;
  title: string;
  description: string | null;
  location: string | null;
  department: string | null;
  salary_range: string | null;
  deadline: string | null;
  employment_type: string | null;
  status: string;
  created_at: string | null;
  applications_count?: number;
  avg_ai_match?: number;
  created_by_id?: string;
}

function formatDate(iso: string | null): string {
  if (!iso) return "No date";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function ActiveJobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const { data } = await apiClient.get<Job[]>("/jobs");
        setJobs(data);
      } catch (err: any) {
        setError(err?.response?.data?.error?.message || "Failed to load jobs");
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900">Active Jobs</h1>
          <p className="text-zinc-500 mt-1">Manage your organization's open positions.</p>
        </div>
        <Link href="/dashboard/new-job">
          <Button className="bg-zinc-900 text-white hover:bg-zinc-800">
            Create Job
          </Button>
        </Link>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          {error}
        </div>
      )}

      <div className="grid gap-6">
        {jobs.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <Briefcase className="h-10 w-10 text-zinc-300" />
              <p className="text-zinc-500">No jobs posted yet. Create your first job opening!</p>
            </CardContent>
          </Card>
        ) : (
          jobs.map((job) => (
            <Card key={job.id} className="transition-all hover:shadow-md hover:border-zinc-300">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-zinc-900">{job.title}</h3>
                      <Badge variant={job.status === 'Open' ? 'default' : 'secondary'} className={job.status === 'Open' ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100' : ''}>
                        {job.status}
                      </Badge>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-600">
                      {job.department && (
                        <span className="flex items-center gap-1.5"><Building className="h-4 w-4" /> {job.department}</span>
                      )}
                      {job.location && (
                        <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" /> {job.location}</span>
                      )}
                      {job.employment_type && (
                        <span className="flex items-center gap-1.5"><Briefcase className="h-4 w-4" /> {job.employment_type}</span>
                      )}
                      {job.salary_range && (
                        <span className="flex items-center gap-1.5"><DollarSign className="h-4 w-4" /> {job.salary_range}</span>
                      )}
                      <span className="flex items-center gap-1.5"><Clock className="h-4 w-4" /> Posted {formatDate(job.created_at)}</span>
                      {job.deadline && (
                        <span className="flex items-center gap-1.5 text-amber-600"><CalendarDays className="h-4 w-4" /> Deadline: {formatDate(job.deadline)}</span>
                      )}
                    </div>

                    <div className="flex items-center gap-6 mt-4 p-3 bg-zinc-50 rounded-lg">
                      <div className="flex flex-col">
                        <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Applications</span>
                        <span className="text-lg font-semibold text-zinc-900">{job.applications_count ?? 0}</span>
                      </div>
                      <div className="h-8 w-px bg-zinc-200"></div>
                      <div className="flex flex-col">
                        <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Avg AI Match</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-zinc-200 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${job.avg_ai_match ?? 0}%` }}></div>
                          </div>
                          <span className="text-sm font-semibold text-zinc-900">{job.avg_ai_match ?? 0}%</span>
                        </div>
                      </div>
                      <div className="h-8 w-px bg-zinc-200"></div>
                      <div className="flex flex-col">
                        <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Recruiter ID</span>
                        <span className="text-sm text-zinc-700 truncate max-w-[120px]" title={job.created_by_id}>{job.created_by_id?.substring(0,8) || "System"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 w-full md:w-auto">
                    <Link href={`/dashboard/jobs/${job.id}`}>
                      <Button className="w-full gap-2 bg-zinc-900 text-white hover:bg-zinc-800">
                        View Details <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <Button variant="outline" size="sm" className="h-9 px-2 flex items-center justify-center gap-1.5 text-xs"><Edit className="h-3.5 w-3.5" /> Edit</Button>
                      <Button variant="outline" size="sm" className="h-9 px-2 flex items-center justify-center gap-1.5 text-xs"><BarChart2 className="h-3.5 w-3.5" /> Analytics</Button>
                      <Button variant="outline" size="sm" className="h-9 px-2 flex items-center justify-center gap-1.5 text-xs"><Copy className="h-3.5 w-3.5" /> Duplicate</Button>
                      <Button variant="outline" size="sm" className="h-9 px-2 flex items-center justify-center gap-1.5 text-xs"><Archive className="h-3.5 w-3.5" /> Archive</Button>
                      <Button variant="outline" size="sm" className="h-9 px-2 flex items-center justify-center gap-1.5 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50"><Trash2 className="h-3.5 w-3.5" /> Delete</Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
