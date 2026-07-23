"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  ArrowLeft, Shield, Clock, User, Filter, FileText, 
  Briefcase, UserCheck, Activity as ActivityIcon
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import { useAuth } from "@/lib/auth-context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  ip_address: string | null;
  occurred_at: string | null;
  metadata: Record<string, unknown> | null;
}

const ACTION_ICONS: Record<string, React.ReactNode> = {
  create: <FileText className="h-4 w-4 text-emerald-500" />,
  update: <UserCheck className="h-4 w-4 text-amber-500" />,
  delete: <FileText className="h-4 w-4 text-rose-500" />,
  login: <User className="h-4 w-4 text-indigo-500" />,
  default: <ActivityIcon className="h-4 w-4 text-zinc-400" />,
};

const ACTION_COLORS: Record<string, string> = {
  create: "bg-emerald-100 text-emerald-800",
  update: "bg-amber-100 text-amber-800",
  delete: "bg-rose-100 text-rose-800",
  login: "bg-indigo-100 text-indigo-800",
};

function getIcon(action: string) {
  const key = Object.keys(ACTION_ICONS).find(k => action.toLowerCase().includes(k));
  return key ? ACTION_ICONS[key] : ACTION_ICONS.default;
}

function getColor(action: string) {
  const key = Object.keys(ACTION_COLORS).find(k => action.toLowerCase().includes(k));
  return key ? ACTION_COLORS[key] : "bg-zinc-100 text-zinc-700";
}

export default function ActivityLogPage() {
  const { getToken } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const token = await getToken();
        if (!token) return;

        const params = new URLSearchParams({ limit: "50", skip: "0" });
        if (actionFilter) params.set("action", actionFilter);
        if (resourceFilter) params.set("resource_type", resourceFilter);

        const res = await fetch(`${API_BASE}/audit/logs?${params.toString()}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setLogs(data.items || []);
          setTotal(data.total || 0);
        }
      } catch (err) {
        console.error("Failed to fetch audit logs", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [getToken, actionFilter, resourceFilter]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Link href="/dashboard" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 mb-2 transition-colors w-fit">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-zinc-900 flex items-center justify-center text-white">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-zinc-900">Activity Log</h1>
            <p className="text-zinc-500">Audit trail of all actions in your organization. {total} total events.</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <Select onValueChange={(v) => setActionFilter(v === "all" ? "" : v)}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by action" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Actions</SelectItem>
            <SelectItem value="create">Create</SelectItem>
            <SelectItem value="update">Update</SelectItem>
            <SelectItem value="delete">Delete</SelectItem>
            <SelectItem value="login">Login</SelectItem>
          </SelectContent>
        </Select>
        <Select onValueChange={(v) => setResourceFilter(v === "all" ? "" : v)}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by resource" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Resources</SelectItem>
            <SelectItem value="job">Jobs</SelectItem>
            <SelectItem value="candidate">Candidates</SelectItem>
            <SelectItem value="application">Applications</SelectItem>
            <SelectItem value="user">Users</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Timeline */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
            </div>
          ) : logs.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-20 text-center">
              <ActivityIcon className="h-10 w-10 text-zinc-300" />
              <p className="text-sm text-zinc-500">No activity logs found.</p>
            </div>
          ) : (
            <div className="divide-y divide-zinc-100">
              {logs.map((log) => (
                <div key={log.id} className="flex items-start gap-4 p-4 hover:bg-zinc-50/50 transition-colors">
                  <div className="mt-1 shrink-0">{getIcon(log.action)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={`text-xs ${getColor(log.action)}`}>{log.action}</Badge>
                      <Badge variant="outline" className="text-xs">{log.resource_type}</Badge>
                    </div>
                    <p className="text-sm text-zinc-700">
                      <span className="font-medium">{log.action}</span> on <span className="font-medium">{log.resource_type}</span>
                      {log.resource_id && <span className="text-zinc-500"> ({log.resource_id.substring(0, 8)}...)</span>}
                    </p>
                    <div className="flex items-center gap-4 mt-1 text-xs text-zinc-400">
                      {log.occurred_at && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(log.occurred_at).toLocaleString()}
                        </span>
                      )}
                      {log.ip_address && <span>IP: {log.ip_address}</span>}
                      {log.user_id && <span>User: {log.user_id.substring(0, 8)}...</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
