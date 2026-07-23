"use client";

import { useState, useEffect } from "react";
import { Bell, Search, User as UserIcon, LogOut, Settings } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { NavigationBreadcrumbs } from "./navigation-breadcrumbs";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Notification {
  id: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

export function TopHeader() {
  const { user, logout, getToken } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        const res = await fetch(`${API_BASE}/notifications?limit=5`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setNotifications(data);
          setUnreadCount(data.filter((n: Notification) => !n.read).length);
        }
      } catch (err) {
        console.error("Failed to fetch notifications", err);
      }
    };
    
    if (user) {
      fetchNotifications();
    }
  }, [user, getToken]);

  const handleMarkAsRead = async (id: string) => {
    try {
      const token = await getToken();
      await fetch(`${API_BASE}/notifications/${id}/read`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const token = await getToken();
      await fetch(`${API_BASE}/notifications/read-all`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-zinc-200 px-4 py-3 sm:px-6 lg:px-8 flex items-center justify-between">
      <div className="flex-1">
        <NavigationBreadcrumbs />
      </div>
      
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="hidden md:flex relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
          <input 
            type="text" 
            placeholder="Search candidates, jobs..." 
            className="pl-9 pr-4 py-2 bg-zinc-100 border-transparent rounded-full text-sm focus:bg-white focus:border-zinc-300 focus:ring-2 focus:ring-indigo-100 transition-all outline-none w-64"
          />
        </div>

        {/* Notifications */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 rounded-full">
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white ring-2 ring-white">
                  {unreadCount}
                </span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-80 p-0">
            <div className="flex items-center justify-between p-4 border-b border-zinc-100">
              <h3 className="font-semibold text-zinc-900">Notifications</h3>
              {unreadCount > 0 && (
                <button onClick={handleMarkAllRead} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
                  Mark all as read
                </button>
              )}
            </div>
            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-sm text-zinc-500">
                  No notifications yet.
                </div>
              ) : (
                notifications.map(n => (
                  <div 
                    key={n.id} 
                    className={`p-4 border-b border-zinc-100 hover:bg-zinc-50 cursor-pointer transition-colors ${!n.read ? 'bg-indigo-50/50' : ''}`}
                    onClick={() => !n.read && handleMarkAsRead(n.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className={`text-sm ${!n.read ? 'font-semibold text-zinc-900' : 'text-zinc-700'}`}>{n.title}</p>
                        <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{n.message}</p>
                      </div>
                      {!n.read && <div className="h-2 w-2 rounded-full bg-indigo-600 shrink-0 mt-1.5" />}
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="p-2 border-t border-zinc-100">
              <Button variant="ghost" className="w-full text-sm text-zinc-600 h-8">View all</Button>
            </div>
          </PopoverContent>
        </Popover>

        {/* User Profile */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full border border-zinc-200">
              <Avatar className="h-8 w-8">
                <AvatarImage src="" alt={user?.email || "User"} />
                <AvatarFallback className="bg-zinc-900 text-white text-xs">
                  {user?.email?.charAt(0).toUpperCase() || "U"}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{user?.email}</p>
                <p className="text-xs leading-none text-zinc-500">{user?.role?.name ?? "User"}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer">
              <UserIcon className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
