import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"

import {useNavigate} from "react-router-dom";
import React from "react";
import type {FC} from "react";


type NavMenuLink = {
  label: string;
  desc?: string;
  href: string;
  ariaLabel: string;
};

export type NavMenuItem = {
  label: string;
  links: NavMenuLink[];
};

export interface NavMenuProps {
  items: NavMenuItem[];
  className?: string;
}

const NavMenu: FC<NavMenuProps> = ({
                                     items,
                                     className,
                                   }) => {

  const navigate = useNavigate();

  const handleNavigation = (path: string) => (e: React.MouseEvent) => {
    if (path.startsWith('/')) { // Ne se déclenche que si le chemin est interne. Sinon, laisse faire le navigateur
      e.preventDefault(); // Bloque le rechargement standard du navigateur
      navigate(path);     // Utilise le routeur React
      window.scrollTo(0, 0); // Remonte en haut de page après le clic
    }
  };

  return (
    <div className={`flex ${className}`}>
      <NavigationMenu>
        <NavigationMenuList>
          {items?.map((item, idx) => (
            <NavigationMenuItem key={idx}>
              <NavigationMenuTrigger className={'bg-transparent'}>{item.label}</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="w-max flex flex-row gap-3">
                  {item.links?.map((link) => (
                    <ListItem href={link.href} key={link.href} title={link.label}
                                        onClick={handleNavigation(link.href)}>{link.desc}</ListItem>
                  ))}
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>
          ))}
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  )
}

function ListItem({
  title,
  children,
  href,
  ...props
}: React.ComponentPropsWithoutRef<"li"> & { href: string }) {
  return (
    <li {...props}>
      <NavigationMenuLink asChild>
        <a href={href}>
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
