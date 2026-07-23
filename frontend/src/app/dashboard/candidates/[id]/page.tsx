"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, Mail, Phone, ExternalLink, FileText, 
  CheckCircle2, XCircle, Calendar, GraduationCap, 
  Briefcase, MessageSquare, Clock
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/lib/auth-context";
import { useQuery } from "@tanstack/react-query";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function CandidateDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  
  const [candidate, setCandidate] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const { getToken } = useAuth();

  const fetchCandidateDetails = async () => {
    const token = await getToken();
    if (!token) throw new Error("No auth token");

    const res = await fetch(`${API_BASE}/candidates/${params.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (!res.ok) throw new Error("Failed to fetch candidate details");
    const data = await res.json();
    return data;
  };

  const fetchApplications = async () => {
    const token = await getToken();
    if (!token) throw new Error("No auth token");

    const res = await fetch(`${API_BASE}/applications?candidate_id=${params.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (!res.ok) throw new Error("Failed to fetch applications");
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  };

  const { data: queryCandidate, isLoading: loadingCandidate, error: errorCandidate } = useQuery({
    queryKey: ['candidate', params.id],
    queryFn: fetchCandidateDetails,
    // Poll every 3 seconds if parsed_data is empty (resume still processing)
    refetchInterval: (query) => {
      if (query.state.data && !query.state.data.parsed_data) return 3000;
      return false;
    }
  });

  const { data: queryApplications, isLoading: loadingApps } = useQuery({
    queryKey: ['applications', params.id],
    queryFn: fetchApplications,
    refetchInterval: (query) => {
      // Poll if any application has no score
      if (query.state.data && query.state.data.some((a: any) => a.score === null)) return 3000;
      return false;
    }
  });

  useEffect(() => {
    if (queryCandidate) setCandidate(queryCandidate);
  }, [queryCandidate]);

  useEffect(() => {
    if (queryApplications) setApplications(queryApplications);
  }, [queryApplications]);

  const loading = loadingCandidate || loadingApps;
  const error = errorCandidate ? "Could not load candidate details." : "";

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="p-8 max-w-7xl mx-auto text-center">
        <h2 className="text-2xl font-bold text-zinc-900">Error</h2>
        <p className="text-zinc-500 mt-2">{error || "Candidate not found"}</p>
        <Link href="/dashboard/applications">
          <Button className="mt-4">Back to Applications</Button>
        </Link>
      </div>
    );
  }

  const parsedData = candidate.parsed_data || {};
  const aiSummary = parsedData.summary || "No AI summary available. Resume might still be processing.";
  const skills = parsedData.skills || [];
  const experience = parsedData.experience || [];
  const education = parsedData.education || [];

  // Use the highest score among their applications as their overall match
  const bestMatch = applications.length > 0 
    ? Math.max(...applications.map(a => (a.score || 0) * 100)) 
    : 0;

  return (
    <div className="p-8 max-w-[1600px] mx-auto h-[calc(100vh-64px)] flex flex-col">
      {/* Header section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 shrink-0">
        <div>
          <Link href="/dashboard/applications" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 mb-2 transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Applications
          </Link>
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-zinc-900 text-white flex items-center justify-center text-xl font-bold">
              {candidate.first_name?.[0]}{candidate.last_name?.[0]}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-zinc-900">{candidate.first_name} {candidate.last_name}</h1>
              <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-600 mt-1">
                <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" /> {candidate.email}</span>
                {candidate.phone && <span className="flex items-center gap-1.5"><Phone className="h-4 w-4" /> {candidate.phone}</span>}
                <Badge variant="outline" className="bg-zinc-50">{candidate.status}</Badge>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end mr-4">
            <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Top AI Match</span>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-24 h-2.5 bg-zinc-200 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: `${Math.min(100, bestMatch)}%` }}></div>
              </div>
              <span className="text-lg font-bold text-zinc-900">{Math.round(bestMatch)}%</span>
            </div>
          </div>
          <Button className="gap-2 bg-zinc-900 text-white hover:bg-zinc-800"><MessageSquare className="h-4 w-4" /> Message</Button>
          <Button variant="outline" className="gap-2"><Calendar className="h-4 w-4" /> Schedule</Button>
          <Button variant="outline" className="gap-2 text-rose-600 hover:text-rose-700 hover:bg-rose-50"><XCircle className="h-4 w-4" /> Reject</Button>
        </div>
      </div>

      <div className="flex-1 grid md:grid-cols-2 gap-6 min-h-0">
        {/* Left Column: Resume Viewer */}
        <Card className="flex flex-col overflow-hidden h-full">
          <CardHeader className="shrink-0 py-4 px-6 border-b border-zinc-100 flex flex-row items-center justify-between bg-zinc-50/50">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <FileText className="h-5 w-5 text-zinc-400" /> Resume Document
            </CardTitle>
            {candidate.resume_url && (
              <Button variant="ghost" size="sm" asChild className="h-8 text-xs text-indigo-600 hover:text-indigo-700">
                <a href={candidate.resume_url} target="_blank" rel="noopener noreferrer">
                  Open in New Tab <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </Button>
            )}
          </CardHeader>
          <CardContent className="flex-1 p-0 relative">
            {candidate.resume_url ? (
              <iframe 
                src={candidate.resume_url} 
                className="absolute inset-0 w-full h-full border-0"
                title="Candidate Resume"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-400 p-6 text-center">
                <FileText className="h-16 w-16 mb-4 text-zinc-200" />
                <p>No resume uploaded for this candidate.</p>
                <Button variant="outline" className="mt-4">Request Resume</Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Column: AI Insights & Activity */}
        <Card className="flex flex-col overflow-hidden h-full">
          <Tabs defaultValue="insights" className="flex-1 flex flex-col h-full">
            <CardHeader className="shrink-0 py-0 px-6 border-b border-zinc-100 bg-zinc-50/50">
              <TabsList className="bg-transparent border-b-0 h-14 space-x-6 pb-0 px-0 w-full justify-start">
                <TabsTrigger value="insights" className="data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent">
                  AI Insights
                </TabsTrigger>
                <TabsTrigger value="experience" className="data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent">
                  Experience & Education
                </TabsTrigger>
                <TabsTrigger value="activity" className="data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent">
                  Activity Feed
                </TabsTrigger>
              </TabsList>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto p-6">
              
              <TabsContent value="insights" className="mt-0 space-y-6">
                <div>
                  <h3 className="text-sm font-bold text-zinc-900 mb-3 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span> AI Summary
                  </h3>
                  <div className="p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl text-sm text-zinc-700 leading-relaxed">
                    {aiSummary}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-zinc-900 mb-3 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span> Extracted Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {skills.length > 0 ? skills.map((skill: string, i: number) => (
                      <Badge key={i} variant="secondary" className="bg-zinc-100 text-zinc-700 hover:bg-zinc-200 border-zinc-200">
                        {skill}
                      </Badge>
                    )) : <p className="text-sm text-zinc-500">No skills parsed.</p>}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="experience" className="mt-0 space-y-8">
                <div>
                  <h3 className="text-sm font-bold text-zinc-900 mb-4 flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-zinc-400" /> Work Experience
                  </h3>
                  {experience.length > 0 ? (
                    <div className="space-y-6">
                      {experience.map((exp: any, i: number) => (
                        <div key={i} className="relative pl-4 border-l-2 border-zinc-200 pb-2">
                          <div className="absolute w-2.5 h-2.5 bg-zinc-200 rounded-full -left-[6px] top-1.5 ring-4 ring-white"></div>
                          <h4 className="font-bold text-zinc-900 text-sm">{exp.title}</h4>
                          <div className="text-sm font-medium text-zinc-700 mt-0.5">{exp.company}</div>
                          <div className="text-xs text-zinc-500 mt-1 flex items-center gap-2">
                            <Clock className="h-3.5 w-3.5" /> {exp.dates || "Unknown"}
                          </div>
                          {exp.description && (
                            <p className="text-sm text-zinc-600 mt-3 whitespace-pre-wrap">{exp.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : <p className="text-sm text-zinc-500 italic">No experience data extracted.</p>}
                </div>

                <div>
                  <h3 className="text-sm font-bold text-zinc-900 mb-4 flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-zinc-400" /> Education
                  </h3>
                  {education.length > 0 ? (
                    <div className="space-y-6">
                      {education.map((edu: any, i: number) => (
                        <div key={i} className="relative pl-4 border-l-2 border-zinc-200 pb-2">
                          <div className="absolute w-2.5 h-2.5 bg-zinc-200 rounded-full -left-[6px] top-1.5 ring-4 ring-white"></div>
                          <h4 className="font-bold text-zinc-900 text-sm">{edu.degree}</h4>
                          <div className="text-sm font-medium text-zinc-700 mt-0.5">{edu.institution}</div>
                          <div className="text-xs text-zinc-500 mt-1 flex items-center gap-2">
                            <Calendar className="h-3.5 w-3.5" /> {edu.year || "Unknown"}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : <p className="text-sm text-zinc-500 italic">No education data extracted.</p>}
                </div>
              </TabsContent>

              <TabsContent value="activity" className="mt-0">
                <div className="space-y-6">
                  {/* Applied Event */}
                  <div className="flex gap-4">
                    <div className="mt-1 h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-900">Candidate created profile</p>
                      <p className="text-xs text-zinc-500">{new Date(candidate.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  
                  {/* Application Events */}
                  {applications.map(app => (
                    <div key={app.id} className="flex gap-4">
                      <div className="mt-1 h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                        <FileText className="h-4 w-4 text-indigo-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-zinc-900">
                          Applied for <Link href={`/dashboard/jobs/${app.job?.id || ''}`} className="text-indigo-600 hover:underline">{app.job?.title || 'Unknown Job'}</Link>
                        </p>
                        <p className="text-sm text-zinc-600 mt-1">Status: <Badge variant="outline">{app.status}</Badge></p>
                        <p className="text-xs text-zinc-500 mt-1">{new Date(app.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>

            </CardContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}
