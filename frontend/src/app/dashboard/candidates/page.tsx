"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Users,
  Search,
  Mail,
  ArrowUpRight,
  UserPlus,
  AlertCircle,
} from "lucide-react";
import { AuthGuard } from "@/components/auth-guard";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Candidate {
  id: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  phone: string | null;
  status: string;
  created_at: string | null;
}

const STATUS_OPTIONS = [
  { value: "all", label: "All Statuses" },
  { value: "New", label: "New" },
  { value: "Applied", label: "Applied" },
  { value: "Screening", label: "Screening" },
  { value: "Interview", label: "Interview" },
  { value: "Offer", label: "Offer" },
  { value: "Hired", label: "Hired" },
  { value: "Rejected", label: "Rejected" },
];

const STATUS_COLORS: Record<string, string> = {
  New: "bg-sky-100 text-sky-700",
  Applied: "bg-indigo-100 text-indigo-700",
  Screening: "bg-violet-100 text-violet-700",
  Interview: "bg-amber-100 text-amber-700",
  Offer: "bg-orange-100 text-orange-700",
  Hired: "bg-emerald-100 text-emerald-700",
  Rejected: "bg-rose-100 text-rose-700",
};

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function CandidatesContent() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const { getToken } = useAuth();

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        setLoading(true);
        const token = getToken();
        if (!token) throw new Error("No token");

        const res = await fetch(`${API_BASE}/candidates?limit=100`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch candidates");
        const data = await res.json();
        setCandidates(data);
      } catch (err: any) {
        setError(err.message || "Failed to load candidates");
      } finally {
        setLoading(false);
      }
    };

    fetchCandidates();
  }, [getToken]);

  const filtered = candidates.filter((c) => {
    const name = `${c.first_name ?? ""} ${c.last_name ?? ""}`.toLowerCase();
    const matchesSearch =
      search === "" ||
      name.includes(search.toLowerCase()) ||
      c.email.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900">Candidates</h1>
          <p className="text-zinc-500 mt-1">
            {loading
              ? "Loading..."
              : `${filtered.length} candidate${filtered.length !== 1 ? "s" : ""}`}
          </p>
        </div>
        <Button className="bg-zinc-900 text-white hover:bg-zinc-800 gap-2 w-fit">
          <UserPlus className="h-4 w-4" />
          Add Candidate
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="h-32 rounded-xl bg-zinc-100 animate-pulse"
            />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 mb-4">
            <Users className="h-8 w-8 text-zinc-300" />
          </div>
          <h3 className="text-base font-semibold text-zinc-700">
            No candidates found
          </h3>
          <p className="text-sm text-zinc-400 mt-1">
            {search || statusFilter !== "all"
              ? "Try adjusting your filters"
              : "No candidates have been added yet"}
          </p>
        </div>
      )}

      {/* Candidates grid */}
      {!loading && filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((candidate) => {
            const initials = `${candidate.first_name?.[0] ?? ""}${candidate.last_name?.[0] ?? ""}`.toUpperCase();
            const fullName = `${candidate.first_name ?? ""} ${candidate.last_name ?? ""}`.trim();
            const statusColor =
              STATUS_COLORS[candidate.status] ??
              "bg-zinc-100 text-zinc-600";

            return (
              <Link
                key={candidate.id}
                href={`/dashboard/candidates/${candidate.id}`}
              >
                <Card className="group cursor-pointer hover:shadow-md hover:border-zinc-300 transition-all">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 text-sm font-semibold text-white shrink-0">
                          {initials || "?"}
                        </div>
                        <div>
                          <p className="font-semibold text-zinc-900">
                            {fullName || "Unknown"}
                          </p>
                          <p className="text-xs text-zinc-500 flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {candidate.email}
                          </p>
                        </div>
                      </div>
                      <ArrowUpRight className="h-4 w-4 text-zinc-300 group-hover:text-zinc-600 transition-colors mt-1" />
                    </div>

                    <div className="flex items-center justify-between mt-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor}`}
                      >
                        {candidate.status}
                      </span>
                      {candidate.created_at && (
                        <span className="text-xs text-zinc-400">
                          {formatDate(candidate.created_at)}
                        </span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function CandidatesPage() {
  return (
    <AuthGuard>
      <CandidatesContent />
    </AuthGuard>
  );
}
