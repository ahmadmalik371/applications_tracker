"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Briefcase, MapPin, Building, DollarSign, CalendarDays } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import { useAuth } from "@/lib/auth-context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function NewJobPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    title: "",
    department: "",
    location: "",
    employment_type: "",
    salary_range: "",
    deadline: "",
    description: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const token = await getToken();
      if (!token) throw new Error("Authentication required");

      const payload = {
        ...formData,
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null,
      };

      const res = await fetch(`${API_BASE}/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to create job");
      }

      const newJob = await res.json();
      router.push(`/dashboard/jobs/${newJob.id}`);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <Link href="/dashboard/jobs" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 mb-2 transition-colors w-fit">
          <ArrowLeft className="h-4 w-4" /> Back to Jobs
        </Link>
        <h1 className="text-3xl font-bold text-zinc-900">Create New Job</h1>
        <p className="text-zinc-500 mt-1">Publish a new open role to your career portal.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Details</CardTitle>
              <CardDescription>Core information about the role.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title" className="text-zinc-900">Job Title *</Label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-3 h-4 w-4 text-zinc-400" />
                  <Input 
                    id="title" 
                    name="title" 
                    placeholder="e.g. Senior Software Engineer" 
                    required
                    className="pl-9"
                    value={formData.title}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <div className="relative">
                    <Building className="absolute left-3 top-3 h-4 w-4 text-zinc-400 z-10" />
                    <Input 
                      id="department" 
                      name="department" 
                      placeholder="e.g. Engineering" 
                      className="pl-9"
                      value={formData.department}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 h-4 w-4 text-zinc-400 z-10" />
                    <Input 
                      id="location" 
                      name="location" 
                      placeholder="e.g. New York, NY or Remote" 
                      className="pl-9"
                      value={formData.location}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="employment_type">Employment Type</Label>
                  <Select onValueChange={(val) => handleSelectChange('employment_type', val)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Full-time">Full-time</SelectItem>
                      <SelectItem value="Part-time">Part-time</SelectItem>
                      <SelectItem value="Contract">Contract</SelectItem>
                      <SelectItem value="Internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="salary_range">Salary Range</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-3 h-4 w-4 text-zinc-400 z-10" />
                    <Input 
                      id="salary_range" 
                      name="salary_range" 
                      placeholder="e.g. $100k - $150k" 
                      className="pl-9"
                      value={formData.salary_range}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="deadline">Application Deadline</Label>
                  <div className="relative">
                    <CalendarDays className="absolute left-3 top-3 h-4 w-4 text-zinc-400 z-10" />
                    <Input 
                      id="deadline" 
                      name="deadline" 
                      type="date"
                      className="pl-9"
                      value={formData.deadline}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Job Description</CardTitle>
              <CardDescription>Detailed description, requirements, and responsibilities.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Textarea 
                  id="description" 
                  name="description" 
                  placeholder="Describe the role, responsibilities, and requirements..." 
                  className="min-h-[250px] resize-y"
                  value={formData.description}
                  onChange={handleChange}
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => router.back()} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="gap-2 bg-zinc-900 text-white hover:bg-zinc-800">
              {loading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-200 border-t-zinc-900" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Create Job
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
