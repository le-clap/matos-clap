import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

import type {FC} from "react";
import React from "react";

import {useHandleNavigation} from "@/hooks/useHandleNavigation.ts";

type NavMenuLink = {
  label: string;
  desc?: string;
  href: string;
  ariaLabel: string;
};

export type NavMenuItem = {
  label: string;
  links: NavMenuLink[]; };

export interface NavMenuProps {
  items: NavMenuItem[];
  className?: string;
}

const NavMenu: FC<NavMenuProps> = ({
                                     items,
                                     className,
                                   }) => {

  const handleNavigation = useHandleNavigation();

  return (
    <div className={`flex ${className}`}>
      <NavigationMenu>
        <NavigationMenuList>
          {items?.map((item, idx) => {
            if (item.links && item.links.length > 1) {
              return (
                <NavigationMenuItem key={idx}>
                  <NavigationMenuTrigger className={'bg-transparent'}>{item.label}</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="w-max flex flex-row gap-3">
                      {item.links?.map((link) => (
                        <ListItem href={link.href} key={link.href} title={link.label} ariaLabel={link.ariaLabel}
                                  onClick={handleNavigation(link.href)}>{link.desc}</ListItem>
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              );
            }
            if (item.links) {
              return (
                <NavigationMenuItem key={idx}>
                  <NavigationMenuLink
                    href={item.links[0].href}
                    onClick={handleNavigation(item.links[0].href)}
                    aria-label={item.links[0].ariaLabel}
                    className={`${navigationMenuTriggerStyle()} bg-transparent`}
                  >
                    {item.label}
                  </NavigationMenuLink>
                </NavigationMenuItem>
              );
            }

            return null;
          })}
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  )
}

function ListItem({
  title,
  children,
  href,
  ariaLabel,
  ...props
}: React.ComponentPropsWithoutRef<"li"> & { href: string; ariaLabel?: string }) {
  return (
    <li {...props}>
      <NavigationMenuLink asChild>
        <a href={href} aria-label={ariaLabel}>
          <div className="flex flex-col gap-1 text-sm">
            <div className="leading-none font-medium">{title}</div>
            <div className="line-clamp-2 text-muted-foreground">{children}</div>
          </div>
        </a>
      </NavigationMenuLink>
    </li>
  )
}

export default NavMenu;
