"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import {
  Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger
} from "@/components/ui/sheet";
import { FileText, MoreHorizontal, Mail, XCircle, CheckCircle2, Filter, Download, Trash2, SlidersHorizontal, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Application {
  id: string;
  status: string;
  score: number | null;
  created_at: string;
  candidate: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  } | null;
  job: {
    id: string;
    title: string;
  } | null;
  ai_explanation?: {
    strengths: string[];
    weaknesses: string[];
    missing_skills: string[];
  };
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { getToken } = useAuth();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const token = await getToken();
        if (!token) throw new Error("No token");

        let url = `${API_BASE}/applications`;
        const params = new URLSearchParams();
        if (statusFilter && statusFilter !== "all") params.append("status", statusFilter);
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }

        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to fetch applications");
        
        const data = await res.json();
        setApplications(Array.isArray(data) ? data : []);
      } catch (err) {
        setError("Failed to load applications");
      } finally {
        setLoading(false);
      }
    };
    
    fetchApplications();
  }, [getToken, statusFilter]);

  const toggleSelectAll = () => {
    if (selectedIds.length === applications.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(applications.map(a => a.id));
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const getStatusColor = (status: string) => {
    switch(status.toLowerCase()) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'shortlisted': return 'bg-indigo-100 text-indigo-800';
      case 'interviewed': return 'bg-amber-100 text-amber-800';
      case 'offered': return 'bg-emerald-100 text-emerald-800';
      case 'hired': return 'bg-emerald-200 text-emerald-900';
      case 'rejected': return 'bg-rose-100 text-rose-800';
      default: return 'bg-zinc-100 text-zinc-800';
    }
  };

  const performBulkAction = (action: string) => {
    // In a real app, this would call bulk update APIs
    alert(`Bulk action '${action}' triggered for ${selectedIds.length} items`);
    setSelectedIds([]);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900">Applications</h1>
          <p className="text-zinc-500 mt-1">Review and manage candidate applications</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            className="gap-2"
            onClick={async () => {
              const token = await getToken();
              if (!token) return;
              const res = await fetch(`${API_BASE}/reports/applications/export?fmt=csv`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'applications.csv';
                a.click();
              }
            }}
          >
            <Download className="h-4 w-4" /> Export CSV
          </Button>
          <Link href="/dashboard/jobs">
            <Button className="bg-zinc-900 text-white hover:bg-zinc-800">
              Go to Jobs
            </Button>
          </Link>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col md:flex-row justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="relative w-64">
                <Filter className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-500" />
                <Input placeholder="Filter by Job Title..." className="pl-9" />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="New">New</SelectItem>
                  <SelectItem value="Shortlisted">Shortlisted</SelectItem>
                  <SelectItem value="Interviewed">Interviewed</SelectItem>
                  <SelectItem value="Offered">Offered</SelectItem>
                  <SelectItem value="Rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
              <Input type="date" value={dateFilter} onChange={(e) => setDateFilter(e.target.value)} className="w-auto" />
            </div>

            {selectedIds.length > 0 && (
              <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-4">
                <span className="text-sm font-medium text-zinc-600 mr-2">{selectedIds.length} selected</span>
                <Button variant="outline" size="sm" onClick={() => performBulkAction('status')} className="gap-1.5"><SlidersHorizontal className="h-4 w-4" /> Change Status</Button>
                <Button variant="outline" size="sm" onClick={() => performBulkAction('email')} className="gap-1.5"><Mail className="h-4 w-4" /> Send Email</Button>
                <Button variant="outline" size="sm" onClick={() => performBulkAction('reject')} className="gap-1.5 text-rose-600 hover:text-rose-700 hover:bg-rose-50"><XCircle className="h-4 w-4" /> Reject</Button>
                <Button variant="destructive" size="sm" onClick={() => performBulkAction('delete')} className="gap-1.5 bg-rose-600"><Trash2 className="h-4 w-4" /> Delete</Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
             <div className="flex h-32 items-center justify-center">
               <div className="h-6 w-6 animate-spin rounded-full border-2 border-zinc-200 border-t-zinc-900" />
             </div>
          ) : error ? (
            <div className="text-center py-8 text-rose-600">{error}</div>
          ) : applications.length === 0 ? (
            <div className="text-center py-12 text-zinc-500">
              <FileText className="h-10 w-10 mx-auto text-zinc-300 mb-3" />
              <p>No applications found matching the current filters.</p>
            </div>
          ) : (
            <div className="rounded-md border border-zinc-200 overflow-hidden">
              <Table>
                <TableHeader className="bg-zinc-50">
                  <TableRow>
                    <TableHead className="w-12 text-center">
                      <Checkbox 
                        checked={selectedIds.length === applications.length && applications.length > 0}
                        onCheckedChange={toggleSelectAll}
                      />
                    </TableHead>
                    <TableHead>Candidate Name</TableHead>
                    <TableHead>Job Title</TableHead>
                    <TableHead>Applied Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>AI Match</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {applications.map((app) => (
                    <TableRow key={app.id} className="hover:bg-zinc-50/50">
                      <TableCell className="text-center">
                        <Checkbox 
                          checked={selectedIds.includes(app.id)}
                          onCheckedChange={() => toggleSelect(app.id)}
                        />
                      </TableCell>
                      <TableCell className="font-medium text-zinc-900">
                        <Link href={`/dashboard/candidates/${app.candidate?.id || ''}`} className="hover:underline">
                          {app.candidate ? `${app.candidate.first_name} ${app.candidate.last_name}` : 'Unknown'}
                        </Link>
                      </TableCell>
                      <TableCell className="text-zinc-600">
                        <Link href={`/dashboard/jobs/${app.job?.id || ''}`} className="hover:underline">
                          {app.job?.title || 'Unknown Job'}
                        </Link>
                      </TableCell>
                      <TableCell className="text-zinc-500">
                        {new Date(app.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={getStatusColor(app.status)}>
                          {app.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-12 h-1.5 bg-zinc-200 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500" style={{ width: `${Math.min(100, (app.score || 0) * 100)}%` }}></div>
                          </div>
                          <span className="text-xs font-semibold">{app.score ? Math.round(app.score * 100) : 0}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-zinc-500 text-sm">
                        Organic
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem asChild>
                              <Link href={`/dashboard/candidates/${app.candidate?.id || ''}`} className="w-full cursor-pointer flex items-center gap-2">
                                <FileText className="h-4 w-4" /> View Profile
                              </Link>
                            </DropdownMenuItem>
                            <Sheet>
                              <SheetTrigger asChild>
                                <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="cursor-pointer flex items-center gap-2 text-indigo-600 focus:text-indigo-700">
                                  <Sparkles className="h-4 w-4" /> Explain Match
                                </DropdownMenuItem>
                              </SheetTrigger>
                              <SheetContent>
                                <SheetHeader>
                                  <SheetTitle>AI Match Explanation</SheetTitle>
                                  <SheetDescription>
                                    Insights for {app.candidate?.first_name} {app.candidate?.last_name} for the {app.job?.title} role.
                                  </SheetDescription>
                                </SheetHeader>
                                <div className="mt-6 space-y-6">
                                  <div>
                                    <h4 className="text-sm font-semibold text-emerald-600 mb-2">Strengths</h4>
                                    <ul className="list-disc pl-5 space-y-1 text-sm text-zinc-700">
                                      {app.ai_explanation?.strengths?.length ? 
                                        app.ai_explanation.strengths.map((s: string, i: number) => <li key={i}>{s}</li>) : 
                                        <li>Not enough data.</li>}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="text-sm font-semibold text-rose-600 mb-2">Weaknesses</h4>
                                    <ul className="list-disc pl-5 space-y-1 text-sm text-zinc-700">
                                      {app.ai_explanation?.weaknesses?.length ? 
                                        app.ai_explanation.weaknesses.map((w: string, i: number) => <li key={i}>{w}</li>) : 
                                        <li>Not enough data.</li>}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="text-sm font-semibold text-amber-600 mb-2">Missing Skills</h4>
                                    <ul className="list-disc pl-5 space-y-1 text-sm text-zinc-700">
                                      {app.ai_explanation?.missing_skills?.length ? 
                                        app.ai_explanation.missing_skills.map((m: string, i: number) => <li key={i}>{m}</li>) : 
                                        <li>Not enough data.</li>}
                                    </ul>
                                  </div>
                                </div>
                              </SheetContent>
                            </Sheet>
                            <DropdownMenuItem className="cursor-pointer flex items-center gap-2">
                              <CheckCircle2 className="h-4 w-4" /> Move Forward
                            </DropdownMenuItem>
                            <DropdownMenuItem className="cursor-pointer flex items-center gap-2 text-rose-600 focus:text-rose-700">
                              <XCircle className="h-4 w-4" /> Reject
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
