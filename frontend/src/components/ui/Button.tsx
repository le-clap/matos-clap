import { Slot } from './Slot';
import { Loader2 } from 'lucide-react';
import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost' | 'outline' | 'danger' | 'subtle';
type Size = 'sm' | 'md' | 'lg' | 'icon' | 'icon-sm';

const variants: Record<Variant, string> = {
  primary:
    'bg-primary text-primary-contrast hover:bg-primary-hover active:bg-primary-strong shadow-sm shadow-brand-900/40',
  secondary:
    'bg-surface-raised text-content border border-border hover:bg-surface-hover hover:border-border-strong',
  outline: 'border border-border-strong text-content hover:bg-surface-raised',
  ghost: 'text-content-muted hover:bg-surface-raised hover:text-content',
  subtle: 'bg-surface-hover text-content hover:bg-ink-700',
  danger:
    'border border-danger/40 bg-danger-bg text-brand-300 hover:bg-primary-strong hover:border-transparent hover:text-white',
};

const sizes: Record<Size, string> = {
  sm: 'h-8 px-3 text-[13px] gap-1.5 rounded-lg',
  md: 'h-10 px-4 text-sm gap-2 rounded-lg',
  lg: 'h-11 px-5 text-[15px] gap-2 rounded-xl',
  icon: 'h-10 w-10 rounded-lg',
  'icon-sm': 'h-8 w-8 rounded-lg',
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  asChild?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      asChild = false,
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    const classes = cn(
      'inline-flex select-none items-center justify-center whitespace-nowrap font-medium transition-colors duration-150 outline-none focus-visible:ring-2 focus-visible:ring-primary/60 focus-visible:ring-offset-0 disabled:pointer-events-none disabled:opacity-50',
      variants[variant],
      sizes[size],
      className,
    );

    // asChild merges styling onto a single child element (e.g. a router Link).
    // It must receive exactly one element child, so the loading spinner is
    // only rendered in the native-button path.
    if (asChild) {
      return (
        <Slot className={classes} {...props}>
          {children}
        </Slot>
      );
    }

    return (
      <button ref={ref} className={classes} disabled={disabled || loading} {...props}>
        {loading && <Loader2 className="size-4 animate-spin" />}
        {children}
      </button>
    );
  },
);
Button.displayName = 'Button';
