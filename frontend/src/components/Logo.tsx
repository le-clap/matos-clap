import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export function Logo({
  to = "/",
  className,
  compact = false,
}: {
  to?: string;
  className?: string;
  compact?: boolean;
}) {
  return (
    <Link
      to={to}
      className={cn("flex items-center gap-2.5 transition-opacity hover:opacity-90", className)}
    >
      <img
        src="/logo-clap.png"
        alt="CLAP"
        className="size-9 rounded-lg object-contain"
      />
      {!compact && (
        <div className="flex flex-col leading-none">
          <span className="text-[15px] font-bold tracking-tight text-content">
            Matos<span className="text-primary"> CLAP</span>
          </span>
          <span className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.14em] text-content-faint">
            Prêt de matériel
          </span>
        </div>
      )}
    </Link>
  );
}
