"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNotifications } from "@/lib/hooks";
import { Clock, Bell, ChevronLeft } from "lucide-react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth-guard";

export default function DashboardNotificationsPage() {
  const { data, isLoading, isError, refetch } = useNotifications(50);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-zinc-50 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-900">Notifications</h1>
            <p className="text-sm text-zinc-500">Recent activity and alerts for your account.</p>
          </div>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-2">
              <ChevronLeft className="h-4 w-4" /> Back
            </Button>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Activity</CardTitle>
            <CardDescription>Notifications are updated in real time.</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((key) => (
                  <div key={key} className="h-16 rounded-lg bg-zinc-100" />
                ))}
              </div>
            ) : isError ? (
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                Failed to load notifications.
                <button onClick={() => refetch()} className="ml-2 text-rose-900 underline">
                  Retry
                </button>
              </div>
            ) : !data || data.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-12 text-center text-sm text-zinc-500">
                <Bell className="h-10 w-10 text-zinc-300" />
                <p>No notifications yet.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {data.map((notification) => (
                  <div key={notification.id} className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-2 text-zinc-700">
                        <Bell className="h-4 w-4" />
                        <span className="font-semibold">{notification.title}</span>
                      </div>
                      <span className="text-xs text-zinc-400">
                        {notification.created_at ? new Date(notification.created_at).toLocaleString() : ""}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-zinc-500">{notification.message}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
    </AuthGuard>
  );
}
