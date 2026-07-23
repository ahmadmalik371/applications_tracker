"use client";

import Link from "next/link";
import {
  Briefcase,
  Users,
  FileText,
  TrendingUp,
  Bell,
  ArrowUpRight,
  Clock,
  ChevronRight,
  AlertCircle,
  UserPlus,
  CheckCircle2,
  Mail,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardStats, useNotifications, useUnreadNotificationCount } from "@/lib/hooks";
import { cn } from "@/lib/utils";
import { AuthGuard } from "@/components/auth-guard";

const PIPELINE_STAGES = [
  { key: "Applied", label: "Applied", color: "bg-sky-500" },
  { key: "Screening", label: "Screening", color: "bg-indigo-500" },
  { key: "Interview", label: "Interview", color: "bg-violet-500" },
  { key: "Offer", label: "Offer", color: "bg-amber-500" },
  { key: "Hired", label: "Hired", color: "bg-emerald-500" },
  { key: "Rejected", label: "Rejected", color: "bg-rose-500" },
];

function DashboardContent() {
  const { data, isLoading, isError, refetch } = useDashboardStats();
  const { data: notifications, isLoading: isNotificationsLoading } = useNotifications(5);
  const { data: unreadCount, isLoading: isUnreadCountLoading } = useUnreadNotificationCount();

  if (isError) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-50 p-8">
        <AlertCircle className="h-10 w-10 text-rose-500" />
        <h2 className="text-lg font-semibold text-zinc-900">Failed to load dashboard</h2>
        <Button onClick={() => refetch()} variant="outline">
          Try again
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <DashboardHeader unreadCount={unreadCount} isUnreadCountLoading={isUnreadCountLoading} />
      <main id="main-content" className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stat cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Active Jobs"
            value={data?.active_jobs}
            total={data?.total_jobs}
            icon={<Briefcase className="h-5 w-5" />}
            accent="bg-sky-50 text-sky-700"
            isLoading={isLoading}
            href="/dashboard/jobs"
          />
          <StatCard
            label="Total Candidates"
            value={data?.total_candidates}
            sublabel={`${data?.new_candidates ?? 0} new`}
            icon={<Users className="h-5 w-5" />}
            accent="bg-emerald-50 text-emerald-700"
            isLoading={isLoading}
            href="/dashboard/candidates"
          />
          <StatCard
            label="Applications"
            value={data?.total_applications}
            icon={<FileText className="h-5 w-5" />}
            accent="bg-amber-50 text-amber-700"
            isLoading={isLoading}
            href="/dashboard/applications"
          />
          <StatCard
            label="New This Week"
            value={data?.new_candidates}
            icon={<TrendingUp className="h-5 w-5" />}
            accent="bg-violet-50 text-violet-700"
            isLoading={isLoading}
            href="/dashboard/candidates?filter=new_this_week"
          />
        </div>

        {/* Pipeline + Analytics */}
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Hiring Pipeline</CardTitle>
              <CardDescription>Applications by stage</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-4">
                  {PIPELINE_STAGES.map((s) => (
                    <Skeleton key={s.key} className="h-12 w-full" />
                  ))}
                </div>
              ) : (
                <PipelineWidget pipeline={data?.pipeline ?? {}} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>Recent activity</CardDescription>
            </CardHeader>
            <CardContent>
              <NotificationsWidget data={notifications} isLoading={isLoading || isNotificationsLoading} />
            </CardContent>
          </Card>
        </div>

        {/* Recent jobs + candidates */}
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <div>
                <CardTitle>Active Jobs</CardTitle>
                <CardDescription>Recently posted positions</CardDescription>
              </div>
              <Button asChild variant="ghost" size="sm" className="gap-1 text-zinc-500">
                <Link href="/dashboard/jobs">
                  View all <ChevronRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              ) : (
                <RecentJobsWidget jobs={data?.recent_jobs ?? []} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Candidates</CardTitle>
                <CardDescription>Latest applicants</CardDescription>
              </div>
              <Button asChild variant="ghost" size="sm" className="gap-1 text-zinc-500">
                <Link href="/dashboard/candidates">
                  View all <ChevronRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              ) : (
                <RecentCandidatesWidget candidates={data?.recent_candidates ?? []} />
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}

function DashboardHeader({
  unreadCount,
  isUnreadCountLoading,
}: {
  unreadCount?: number;
  isUnreadCountLoading: boolean;
}) {
  return (
    <header className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-zinc-900">Recruiter Dashboard</h1>
          <p className="text-sm text-zinc-500">AI-powered applicant tracking</p>
        </div>
        <div className="flex items-center gap-3">
          <Button asChild variant="outline" size="sm" className="gap-2">
            <Link href="/dashboard/notifications">
              <Bell className="h-4 w-4" />
              <span className="hidden sm:inline">Notifications</span>
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-xs font-semibold text-white">
                {isUnreadCountLoading ? "..." : unreadCount ?? 0}
              </span>
            </Link>
          </Button>
          <Button asChild size="sm" className="gap-2 bg-zinc-900 text-white hover:bg-zinc-800">
            <Link href="/dashboard/new-job">
              <Briefcase className="h-4 w-4" />
              <span className="hidden sm:inline">New Job</span>
            </Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

function StatCard({
  label,
  value,
  total,
  sublabel,
  icon,
  accent,
  isLoading,
  href,
}: {
  label: string;
  value?: number;
  total?: number;
  sublabel?: string;
  icon: React.ReactNode;
  accent: string;
  isLoading: boolean;
  href?: string;
}) {
  const content = (
    <Card className={cn("overflow-hidden transition-all hover:shadow-md h-full", href && "hover:border-zinc-300 hover:ring-1 hover:ring-zinc-200")}>
      <CardContent className="flex items-center gap-4">
        <div className={cn("flex h-12 w-12 items-center justify-center rounded-lg", accent)}>
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-zinc-500">{label}</span>
          {isLoading ? (
            <Skeleton className="mt-1 h-7 w-16" />
          ) : (
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-zinc-900">{value ?? 0}</span>
              {total !== undefined && (
                <span className="text-sm text-zinc-400">/ {total}</span>
              )}
              {sublabel && (
                <span className="text-xs text-zinc-500">{sublabel}</span>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (href) {
    return <Link href={href} className="block h-full">{content}</Link>;
  }
  return content;
}

function PipelineWidget({ pipeline }: { pipeline: Record<string, number> }) {
  const total = Object.values(pipeline).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="space-y-4">
      {PIPELINE_STAGES.map((stage) => {
        const count = pipeline[stage.key] ?? 0;
        const pct = (count / total) * 100;
        return (
          <div key={stage.key} className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-zinc-700">{stage.label}</span>
              <span className="text-zinc-500">{count}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-100">
              <div
                className={cn("h-full rounded-full transition-all duration-700 ease-out", stage.color)}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
      {total === 1 && (
        <p className="py-4 text-center text-sm text-zinc-400">No applications yet</p>
      )}
    </div>
  );
}

function NotificationsWidget({
  data,
  isLoading,
}: {
  data: Array<{
    id: string;
    organization_id: string;
    user_id?: string;
    channel: string;
    title: string;
    message: string;
    status: string;
    read: boolean;
    created_at: string | null;
  }> | undefined;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  const items: Array<{ icon: React.ReactNode; title: string; message: string; time: string }> = [];

  for (const notification of data ?? []) {
    items.push({
      icon: notification.channel === "email" ? (
        <Mail className="h-4 w-4 text-sky-600" />
      ) : (
        <Bell className="h-4 w-4 text-emerald-600" />
      ),
      title: notification.title,
      message: notification.message,
      time: notification.created_at ? formatRelative(notification.created_at) : "",
    });
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 text-center">
        <Bell className="h-8 w-8 text-zinc-300" />
        <p className="text-sm text-zinc-400">No recent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.slice(0, 5).map((item, i) => (
        <div key={i} className="flex items-start gap-3 rounded-lg p-2 transition-colors hover:bg-zinc-50">
          <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full bg-zinc-100">
            {item.icon}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-zinc-700">{item.title}</p>
            <p className="text-sm text-zinc-500">{item.message}</p>
            {item.time && (
              <p className="flex items-center gap-1 text-xs text-zinc-400">
                <Clock className="h-3 w-3" /> {item.time}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function RecentJobsWidget({
  jobs,
}: {
  jobs: Array<{
    id: string;
    title: string;
    status: string;
    location: string | null;
    created_at: string | null;
  }>;
}) {
  if (jobs.length === 0) {
    return <EmptyState message="No jobs posted yet" />;
  }

  return (
    <div className="space-y-2">
      {jobs.map((job) => (
        <Link
          key={job.id}
          href={`/dashboard/jobs/${job.id}`}
          className="group flex items-center justify-between rounded-lg border border-zinc-100 p-3 transition-colors hover:border-zinc-200 hover:bg-zinc-50 block"
        >
          <div className="flex flex-col gap-1">
            <span className="font-medium text-zinc-900">{job.title}</span>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              {job.location && <span>{job.location}</span>}
              {job.created_at && <span>· {formatRelative(job.created_at)}</span>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={job.status} />
            <ArrowUpRight className="h-4 w-4 text-zinc-300 transition-colors group-hover:text-zinc-600" />
          </div>
        </Link>
      ))}
    </div>
  );
}

function RecentCandidatesWidget({
  candidates,
}: {
  candidates: Array<{
    id: string;
    first_name: string | null;
    last_name: string | null;
    email: string;
    status: string;
    created_at: string | null;
  }>;
}) {
  if (candidates.length === 0) {
    return <EmptyState message="No candidates yet" />;
  }

  return (
    <div className="space-y-2">
      {candidates.map((c) => {
        const initials = `${c.first_name?.[0] ?? ""}${c.last_name?.[0] ?? ""}`.toUpperCase();
        return (
          <Link
            key={c.id}
            href={`/dashboard/candidates/${c.id}`}
            className="group flex items-center justify-between rounded-lg border border-zinc-100 p-3 transition-colors hover:border-zinc-200 hover:bg-zinc-50 block"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 text-xs font-semibold text-white">
                {initials}
              </div>
              <div className="flex flex-col">
                <span className="font-medium text-zinc-900">
                  {`${c.first_name ?? ""} ${c.last_name ?? ""}`.trim()}
                </span>
                <span className="text-xs text-zinc-500">{c.email}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={c.status} />
              <ArrowUpRight className="h-4 w-4 text-zinc-300 transition-colors group-hover:text-zinc-600" />
            </div>
          </Link>
        );
      })}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variant = (() => {
    switch (status) {
      case "Open":
      case "Hired":
        return "success" as const;
      case "Interview":
        return "default" as const;
      case "Rejected":
      case "Closed":
        return "destructive" as const;
      case "Review":
      case "Offer":
        return "warning" as const;
      default:
        return "secondary" as const;
    }
  })();
  return <Badge variant={variant}>{status}</Badge>;
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-2 py-8 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100">
        <FileText className="h-6 w-6 text-zinc-300" />
      </div>
      <p className="text-sm text-zinc-400">{message}</p>
    </div>
  );
}

function formatRelative(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString();
}
