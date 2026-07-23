import * as React from "react";
import { cn } from "@/lib/utils";

type TabsContentProps = React.ComponentProps<"div"> & {
  value?: string;
};

function Tabs({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="tabs" className={cn("flex flex-col gap-2", className)} {...props} />;
}

function TabsList({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="tabs-list"
      className={cn("inline-flex h-10 items-center justify-center rounded-lg bg-zinc-100 p-1 text-zinc-500", className)}
      {...props}
    />
  );
}

function TabsTrigger({ className, ...props }: React.ComponentProps<"button">) {
  return (
    <button
      type="button"
      data-slot="tabs-trigger"
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-900 disabled:pointer-events-none disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}

function TabsContent({ className, value, ...props }: TabsContentProps) {
  return (
    <div
      data-slot="tabs-content"
      data-value={value}
      className={cn("mt-2", className)}
      {...props}
    />
  );
}

export { Tabs, TabsList, TabsTrigger, TabsContent };
