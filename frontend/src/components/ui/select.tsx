import * as React from "react";
import { cn } from "@/lib/utils";

type SelectProps = React.ComponentProps<"select"> & {
  onValueChange?: (value: string) => void;
};

function Select({ className, onValueChange, onChange, children, ...props }: SelectProps) {
  return (
    <select
      data-slot="select"
      className={cn("rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm", className)}
      {...props}
      onChange={(event) => {
        onChange?.(event);
        onValueChange?.(event.target.value);
      }}
    >
      {children}
    </select>
  );
}

function SelectTrigger({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="select-trigger"
      className={cn(
        "flex h-9 items-center justify-between rounded-lg border border-zinc-300 bg-transparent px-3 py-2 text-sm text-zinc-900 shadow-sm",
        className
      )}
      {...props}
    />
  );
}

type SelectValueProps = React.ComponentProps<"span"> & {
  placeholder?: string;
};

function SelectValue({ className, placeholder, children, ...props }: SelectValueProps) {
  return (
    <span data-slot="select-value" className={cn(className)} {...props}>
      {children ?? placeholder}
    </span>
  );
}

function SelectContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="select-content"
      className={cn("rounded-lg border border-zinc-200 bg-white shadow-sm", className)}
      {...props}
    />
  );
}

function SelectItem({ className, value, ...props }: React.ComponentProps<"option">) {
  return (
    <option
      data-slot="select-item"
      value={value}
      className={cn(className)}
      {...props}
    />
  );
}

export {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
};