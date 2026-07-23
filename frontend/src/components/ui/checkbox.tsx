import * as React from "react";
import { cn } from "@/lib/utils";

type CheckboxProps = React.ComponentProps<"input"> & {
  onCheckedChange?: (checked: boolean) => void;
};

function Checkbox({ className, onCheckedChange, onChange, ...props }: CheckboxProps) {
  return (
    <input
      type="checkbox"
      data-slot="checkbox"
      className={cn(
        "h-4 w-4 rounded border border-zinc-300 text-zinc-900 focus:ring-zinc-900",
        className
      )}
      {...props}
      onChange={(event) => {
        onChange?.(event);
        onCheckedChange?.(event.target.checked);
      }}
    />
  );
}

export { Checkbox };
