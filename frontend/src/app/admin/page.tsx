"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Building2,
  Users,
  Briefcase,
  UserCheck,
  CreditCard,
  Flag,
  Megaphone,
  Settings,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";

export default function SuperAdminPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => apiClient.get("/admin/stats").then((r) => r.data),
  });

  const { data: plans } = useQuery({
    queryKey: ["admin-plans"],
    queryFn: () => apiClient.get("/admin/plans").then((r) => r.data),
  });

  const { data: flags } = useQuery({
    queryKey: ["admin-flags"],
    queryFn: () => apiClient.get("/admin/feature-flags").then((r) => r.data),
  });

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-zinc-900">Super Admin Dashboard</h1>
            <p className="text-sm text-zinc-500">Platform-wide management</p>
          </div>
          <Badge variant="default" className="bg-zinc-900 text-white">Super Admin</Badge>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard label="Organizations" value={stats?.organizations} icon={<Building2 className="h-5 w-5" />} accent="bg-sky-50 text-sky-700" isLoading={isLoading} />
          <StatCard label="Users" value={stats?.users} icon={<Users className="h-5 w-5" />} accent="bg-emerald-50 text-emerald-700" isLoading={isLoading} />
          <StatCard label="Jobs" value={stats?.jobs} icon={<Briefcase className="h-5 w-5" />} accent="bg-amber-50 text-amber-700" isLoading={isLoading} />
          <StatCard label="Candidates" value={stats?.candidates} icon={<UserCheck className="h-5 w-5" />} accent="bg-violet-50 text-violet-700" isLoading={isLoading} />
          <StatCard label="Active Subs" value={stats?.active_subscriptions} icon={<CreditCard className="h-5 w-5" />} accent="bg-rose-50 text-rose-700" isLoading={isLoading} />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>SaaS Plans</CardTitle>
              <CardDescription>Subscription tiers</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
              ) : (
                <div className="space-y-2">
                  {plans?.map((plan: { id: string; name: string; max_users: number; max_ai_requests: number; max_storage_mb: number; price_cents: number; is_active: boolean }) => (
                    <div key={plan.id} className="flex items-center justify-between rounded-lg border border-zinc-100 p-3">
                      <div>
                        <span className="font-medium text-zinc-900">{plan.name}</span>
                        <p className="text-xs text-zinc-500">
                          {plan.max_users} users · {plan.max_ai_requests} AI reqs · {plan.max_storage_mb}MB
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-semibold text-zinc-900">
                          ${(plan.price_cents / 100).toFixed(2)}/mo
                        </span>
                        <Badge variant={plan.is_active ? "success" : "secondary"} className="ml-2">
                          {plan.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Feature Flags</CardTitle>
              <CardDescription>Module toggles</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
              ) : (
                <div className="space-y-2">
                  {flags?.map((flag: { id: string; name: string; module: string; is_enabled: boolean }) => (
                    <div key={flag.id} className="flex items-center justify-between rounded-lg border border-zinc-100 p-3">
                      <div className="flex items-center gap-3">
                        <Flag className="h-4 w-4 text-zinc-400" />
                        <div>
                          <span className="font-medium text-zinc-900">{flag.name}</span>
                          <p className="text-xs text-zinc-500">{flag.module}</p>
                        </div>
                      </div>
                      <Badge variant={flag.is_enabled ? "success" : "destructive"}>
                        {flag.is_enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  accent,
  isLoading,
}: {
  label: string;
  value?: number;
  icon: React.ReactNode;
  accent: string;
  isLoading: boolean;
}) {
  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-md">
      <CardContent className="flex items-center gap-4">
        <div className={cn("flex h-12 w-12 items-center justify-center rounded-lg", accent)}>
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-zinc-500">{label}</span>
          {isLoading ? (
            <Skeleton className="mt-1 h-7 w-16" />
          ) : (
            <span className="text-2xl font-bold text-zinc-900">{value ?? 0}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
