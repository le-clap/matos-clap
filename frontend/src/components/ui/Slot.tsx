import {
  Children,
  cloneElement,
  isValidElement,
  type HTMLAttributes,
  type ReactElement,
} from "react";
import { cn } from "@/lib/utils";

/**
 * Minimal `asChild` helper: merges the given props (notably `className`) onto a
 * single React element child instead of rendering a wrapper element.
 */
export function Slot({
  children,
  className,
  ...props
}: HTMLAttributes<HTMLElement>) {
  if (!isValidElement(children)) {
    return null;
  }
  const child = Children.only(children) as ReactElement<
    HTMLAttributes<HTMLElement>
  >;
  return cloneElement(child, {
    ...props,
    ...child.props,
    className: cn(className, child.props.className),
  });
}
