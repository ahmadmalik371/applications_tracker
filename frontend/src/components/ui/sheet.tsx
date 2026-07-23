import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

function Sheet({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="sheet" className={cn(className)} {...props} />;
}

function SheetTrigger({ className, asChild = false, ...props }: React.ComponentProps<"button"> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      type={asChild ? undefined : "button"}
      data-slot="sheet-trigger"
      className={cn("text-left", className)}
      {...props}
    />
  );
}

function SheetContent({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="sheet-content" className={cn("rounded-lg border bg-white p-4 shadow-lg", className)} {...props} />;
}

function SheetHeader({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="sheet-header" className={cn("flex flex-col gap-1.5", className)} {...props} />;
}

function SheetTitle({ className, ...props }: React.ComponentProps<"h2">) {
  return <h2 data-slot="sheet-title" className={cn("text-lg font-semibold", className)} {...props} />;
}

function SheetDescription({ className, ...props }: React.ComponentProps<"p">) {
  return <p data-slot="sheet-description" className={cn("text-sm text-zinc-500", className)} {...props} />;
}

export { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription };
