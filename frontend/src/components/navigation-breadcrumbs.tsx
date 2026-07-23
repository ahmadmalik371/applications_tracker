"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

export function NavigationBreadcrumbs() {
  const pathname = usePathname();
  
  if (!pathname || pathname === "/dashboard") {
    return (
      <nav className="flex text-sm text-zinc-500" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-1 md:space-x-3">
          <li className="inline-flex items-center">
            <span className="inline-flex items-center text-zinc-700 font-medium">
              <Home className="w-4 h-4 mr-2" />
              Dashboard
            </span>
          </li>
        </ol>
      </nav>
    );
  }

  // Generate paths like /dashboard/jobs/123-abc -> Dashboard > Jobs > 123-abc
  const segments = pathname.split("/").filter(Boolean);
  
  return (
    <nav className="flex text-sm text-zinc-500" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-3">
        {segments.map((segment, index) => {
          const isLast = index === segments.length - 1;
          const href = "/" + segments.slice(0, index + 1).join("/");
          
          // Capitalize first letter and format
          const title = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');

          return (
            <li key={href} className="inline-flex items-center">
              {index > 0 && <ChevronRight className="w-4 h-4 text-zinc-400 mx-1" />}
              {isLast ? (
                <span className="text-zinc-900 font-medium" aria-current="page">
                  {index === 0 && <Home className="w-4 h-4 mr-2 inline" />}
                  {title}
                </span>
              ) : (
                <Link
                  href={href}
                  className="inline-flex items-center text-zinc-500 hover:text-zinc-900 transition-colors"
                >
                  {index === 0 && <Home className="w-4 h-4 mr-2" />}
                  {title}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
