"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  FileText,
  Calendar,
  Settings,
  Search,
  MessageSquare,
  BarChart2,
  Bell,
  Shield
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Jobs", href: "/dashboard/jobs", icon: Briefcase },
  { name: "Applications", href: "/dashboard/applications", icon: FileText },
  { name: "Candidates", href: "/dashboard/candidates", icon: Users },
  { name: "Interviews", href: "/dashboard/interviews", icon: Calendar },
  { name: "AI Assistant", href: "/dashboard/ai-assistant", icon: MessageSquare },
  { name: "Search", href: "/dashboard/search", icon: Search },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart2 },
  { name: "Activity Log", href: "/dashboard/activity", icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r border-zinc-200 bg-white">
      <div className="flex h-16 items-center px-6 border-b border-zinc-200">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 text-white font-bold">
            A
          </div>
          <span className="text-xl font-bold tracking-tight text-zinc-900">AI-ATS</span>
        </Link>
      </div>
      
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== "/dashboard");
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-zinc-100 text-zinc-900"
                  : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-zinc-900" : "text-zinc-400 group-hover:text-zinc-500"
                )}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      <div className="border-t border-zinc-200 p-4">
        <Link
          href="/dashboard/settings"
          className="group flex items-center rounded-md px-3 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-50 hover:text-zinc-900"
        >
          <Settings className="mr-3 h-5 w-5 text-zinc-400 group-hover:text-zinc-500" />
          Settings
        </Link>
      </div>
    </div>
  );
}
