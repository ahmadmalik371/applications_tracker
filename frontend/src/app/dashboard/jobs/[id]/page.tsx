"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, Edit, Copy, Archive, Trash2, 
  MapPin, Clock, Building, DollarSign, CalendarDays, 
  Briefcase, CheckCircle2, XCircle, Users, BarChart2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function JobDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  
  const [job, setJob] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        const token = await getToken();
        if (!token) throw new Error("No auth token");

        const res = await fetch(`${API_BASE}/jobs/${params.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to fetch job details");
        const jobData = await res.json();
        setJob(jobData);

        // Fetch applications for this job
        const appsRes = await fetch(`${API_BASE}/applications?job_id=${params.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (appsRes.ok) {
          const appsData = await appsRes.json();
          setApplications(Array.isArray(appsData) ? appsData : []);
        }
      } catch (err) {
        console.error(err);
        setError("Could not load job details.");
      } finally {
        setLoading(false);
      }
    };
    
    if (params.id) {
      fetchJobDetails();
    }
  }, [params.id, getToken]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="p-8 max-w-7xl mx-auto text-center">
        <h2 className="text-2xl font-bold text-zinc-900">Error</h2>
        <p className="text-zinc-500 mt-2">{error || "Job not found"}</p>
        <Link href="/dashboard/jobs">
          <Button className="mt-4">Back to Jobs</Button>
        </Link>
      </div>
    );
  }

  // Calculate application stats
  const stats = {
    total: applications.length,
    new: applications.filter(a => a.status === 'New').length,
    shortlisted: applications.filter(a => a.status === 'Shortlisted').length,
    interviewed: applications.filter(a => a.status === 'Interviewed').length,
    offered: applications.filter(a => a.status === 'Offered').length,
    hired: applications.filter(a => a.status === 'Hired').length,
    rejected: applications.filter(a => a.status === 'Rejected').length,
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4">
        <div>
          <Link href="/dashboard/jobs" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 mb-4 transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Jobs
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-zinc-900">{job.title}</h1>
            <Badge className={job.status === 'Open' ? 'bg-emerald-100 text-emerald-800' : ''}>{job.status}</Badge>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-600 mt-3">
            {job.department && <span className="flex items-center gap-1.5"><Building className="h-4 w-4" /> {job.department}</span>}
            {job.location && <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" /> {job.location}</span>}
            {job.employment_type && <span className="flex items-center gap-1.5"><Briefcase className="h-4 w-4" /> {job.employment_type}</span>}
            {job.salary_range && <span className="flex items-center gap-1.5"><DollarSign className="h-4 w-4" /> {job.salary_range}</span>}
            {job.deadline && <span className="flex items-center gap-1.5 text-amber-600"><CalendarDays className="h-4 w-4" /> Deadline: {new Date(job.deadline).toLocaleDateString()}</span>}
            <span className="flex items-center gap-1.5"><Clock className="h-4 w-4" /> Posted: {new Date(job.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2"><Edit className="h-4 w-4" /> Edit</Button>
          <Button variant="outline" size="sm" className="gap-2"><Copy className="h-4 w-4" /> Duplicate</Button>
          <Button variant="outline" size="sm" className="gap-2"><Archive className="h-4 w-4" /> Archive</Button>
          <Button variant="destructive" size="sm" className="gap-2 bg-rose-600 hover:bg-rose-700"><Trash2 className="h-4 w-4" /> Delete</Button>
        </div>
      </div>

      {/* Analytics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Total</p>
            <p className="text-2xl font-bold text-zinc-900 mt-1">{stats.total}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Shortlisted</p>
            <p className="text-2xl font-bold text-indigo-600 mt-1">{stats.shortlisted}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Interviewed</p>
            <p className="text-2xl font-bold text-amber-600 mt-1">{stats.interviewed}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Offered</p>
            <p className="text-2xl font-bold text-emerald-600 mt-1">{stats.offered}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Hired</p>
            <p className="text-2xl font-bold text-emerald-700 mt-1">{stats.hired}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Rejected</p>
            <p className="text-2xl font-bold text-rose-600 mt-1">{stats.rejected}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Left Column: Job Details */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Job Description</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-zinc max-w-none text-sm text-zinc-700 whitespace-pre-wrap">
                {job.description || "No description provided."}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Requirements & Qualifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-zinc-900 mb-2">Experience & Education</h4>
                <div className="flex gap-4">
                  <Badge variant="secondary">{job.experience_level || "Any Experience"}</Badge>
                  <Badge variant="secondary">{job.education_level || "Any Education"}</Badge>
                </div>
              </div>
              
              {job.requirements && (
                <div>
                  <h4 className="text-sm font-semibold text-zinc-900 mb-2">Required Skills</h4>
                  <ul className="list-disc pl-5 space-y-1 text-sm text-zinc-700">
                    {Array.isArray(job.requirements) ? job.requirements.map((req: string, i: number) => <li key={i}>{req}</li>) : <li>{job.requirements}</li>}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Candidates Pipeline */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Recent Candidates</CardTitle>
              <Link href={`/dashboard/jobs/${params.id}/pipeline`}>
                <Button variant="ghost" size="sm" className="text-indigo-600">View All Pipeline</Button>
              </Link>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="h-8 w-8 text-zinc-300 mx-auto mb-2" />
                  <p className="text-sm text-zinc-500">No applications yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {applications.slice(0, 5).map(app => (
                    <div key={app.id} className="flex items-center justify-between p-3 rounded-lg border border-zinc-100 hover:bg-zinc-50 cursor-pointer transition-colors" onClick={() => router.push(`/dashboard/candidates/${app.candidate?.id}`)}>
                      <div>
                        <p className="text-sm font-medium text-zinc-900">{app.candidate?.first_name} {app.candidate?.last_name}</p>
                        <p className="text-xs text-zinc-500">{new Date(app.created_at).toLocaleDateString()}</p>
                      </div>
                      <Badge variant="outline" className={
                        app.status === 'Shortlisted' ? 'border-indigo-200 text-indigo-700 bg-indigo-50' :
                        app.status === 'Rejected' ? 'border-rose-200 text-rose-700 bg-rose-50' :
                        app.status === 'Hired' ? 'border-emerald-200 text-emerald-700 bg-emerald-50' :
                        'border-zinc-200 text-zinc-700 bg-zinc-50'
                      }>
                        {app.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Hiring Manager</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-zinc-200 flex items-center justify-center text-zinc-600 font-bold">
                  {job.created_by_id ? job.created_by_id.substring(0, 2).toUpperCase() : "HM"}
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-900">User ID: {job.created_by_id || "System"}</p>
                  <p className="text-xs text-zinc-500">Recruiter / Hiring Manager</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
