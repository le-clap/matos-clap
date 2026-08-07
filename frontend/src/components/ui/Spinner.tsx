import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Spinner({ className }: { className?: string }) {
  return <Loader2 className={cn('size-5 animate-spin text-primary', className)} />;
}

export function PageSpinner({ label }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-content-faint">
      <Spinner className="size-7" />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}
