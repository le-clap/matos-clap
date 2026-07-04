import { initials } from "@/lib/format";
import { cn } from "@/lib/utils";

const sizes = {
  sm: "size-7 text-[11px]",
  md: "size-9 text-xs",
  lg: "size-11 text-sm",
};

export function Avatar({
  name,
  size = "md",
  className,
}: {
  name: string;
  size?: keyof typeof sizes;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-700 to-brand-900 font-semibold text-white ring-1 ring-inset ring-white/10",
        sizes[size],
        className,
      )}
      title={name}
    >
      {initials(name)}
    </div>
  );
}
