import ShinyText from './ShinyText';
import React, { useLayoutEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { GoArrowUpRight } from 'react-icons/go';

type CardNavLink = {
  label: string;
  href: string;
  ariaLabel: string;
};

export type CardNavItem = {
  label: string;
  bgColor: string;
  textColor: string;
  links: CardNavLink[];
};

export interface CardNavProps {
  logo?: string; // Made optional to prevent crashes if missing
  logoAlt?: string;
  items: CardNavItem[];
  className?: string;
  ease?: string;
  baseColor?: string;
  menuColor?: string;
  buttonBgColor?: string;
  buttonTextColor?: string;
}

const CardNav: React.FC<CardNavProps> = ({
  logo,
  logoAlt = 'Logo',
  items,
  className = '',
  ease = 'power3.out',
  baseColor = '#fff',
  menuColor = '#000',
  buttonBgColor = '#000',
  buttonTextColor = '#fff'
}) => {
  const [isHamburgerOpen, setIsHamburgerOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const navRef = useRef<HTMLDivElement | null>(null);
  const cardsRef = useRef<HTMLDivElement[]>([]);
  const tlRef = useRef<gsap.core.Timeline | null>(null);

  // Height calculation logic
  const calculateHeight = () => {
    // 1. Mobile Calculation
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    if (isMobile && navRef.current) {
      const contentEl = navRef.current.querySelector('.card-nav-content') as HTMLElement;
      if (contentEl) {
        // Temporarily force visibility to measure true height
        const originalStyle = {
            visibility: contentEl.style.visibility,
            position: contentEl.style.position,
            height: contentEl.style.height,
            display: contentEl.style.display
        };

        contentEl.style.visibility = 'visible';
        contentEl.style.position = 'absolute';
        contentEl.style.height = 'auto';
        contentEl.style.display = 'flex'; // Ensure flex calculation works

        const contentHeight = contentEl.scrollHeight;

        // Revert styles
        contentEl.style.visibility = originalStyle.visibility;
        contentEl.style.position = originalStyle.position;
        contentEl.style.height = originalStyle.height;
        contentEl.style.display = originalStyle.display || '';

        return 60 + contentHeight + 16; // Top bar (60) + Content + Padding
      }
    }
    // 2. Desktop Default
    return 260;
  };

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
        // Initial setup
        gsap.set(navRef.current, { height: 60, overflow: 'hidden' });
        gsap.set(cardsRef.current, { y: 50, opacity: 0 });

        // Create Timeline
        const tl = gsap.timeline({ paused: true });

        tl.to(navRef.current, {
          height: () => calculateHeight(), // Use function wrapper to ensure recalc
          duration: 0.4,
          ease
        });

        tl.to(cardsRef.current, {
            y: 0,
            opacity: 1,
            duration: 0.4,
            ease,
            stagger: 0.08
        }, '-=0.2');

        tlRef.current = tl;
    }, navRef); // Scope to navRef

    return () => ctx.revert(); // Cleanup GSAP on unmount
  }, [ease, items]);

  const toggleMenu = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent clicks from bubbling up

    if (!tlRef.current) return;

    if (!isExpanded) {
      setIsHamburgerOpen(true);
      setIsExpanded(true);
      tlRef.current.play();
    } else {
      setIsHamburgerOpen(false);
      // Use logic to update state after animation
      tlRef.current.reverse().then(() => {
          setIsExpanded(false);
      });
    }
  };

  const setCardRef = (i: number) => (el: HTMLDivElement | null) => {
    if (el) cardsRef.current[i] = el;
  };

  return (
    <div
      className={`card-nav-container absolute left-1/2 -translate-x-1/2 w-[90%] max-w-200 z-50 top-[1.2em] md:top-[4em] ${className}`}
    >
      <nav
        ref={navRef}
        className={`card-nav block p-0 rounded-xl shadow-2xl relative overflow-hidden will-change-[height]`}
        style={{ backgroundColor: baseColor }}
      >
        {/* TOP BAR */}
        <div className="card-nav-top absolute inset-x-0 top-0 h-15 flex items-center justify-between p-2 pl-[1.1rem] z-20 pointer-events-auto">

          {/* HAMBURGER BUTTON */}
          <div
            className={`hamburger-menu group h-full flex flex-col items-center justify-center cursor-pointer gap-1.5 order-2 md:order-0 w-10 z-30`}
            onClick={toggleMenu}
            role="button"
            aria-label={isExpanded ? 'Close menu' : 'Open menu'}
            tabIndex={0}
            style={{ color: menuColor }}
          >
            <div
              className={`w-6.5 h-0.5 bg-current transition-transform duration-300 ease-in-out ${
                isHamburgerOpen ? 'translate-y-1 rotate-45' : ''
              }`}
            />
            <div
              className={`w-6.5 h-0.5 bg-current transition-transform duration-300 ease-in-out ${
                isHamburgerOpen ? '-translate-y-1 -rotate-45' : ''
              }`}
            />
          </div>

          {/* LOGO */}
          <div className="logo-container flex items-center md:absolute md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2 order-1 md:order-0 pointer-events-none">
            {logo && <img src={logo} alt={logoAlt} className="h-7 object-contain" />}
          </div>

          <div>
            <ShinyText
              text="CLAP"
              speed={4}
              delay={0}
              color="#f01826"
              shineColor="#ffffff"
              spread={140}
              direction="left"
              yoyo={false}
              pauseOnHover={false}
              disabled={false}
              className={"font-heading text-4xl "}
            />
          </div>

          {/* CTA BUTTON */}
          <button
            type="button"
            className="hidden md:inline-flex border-0 rounded-lg px-4 items-center h-10 font-medium cursor-pointer transition-colors duration-300 hover:opacity-90 active:scale-95"
            style={{ backgroundColor: buttonBgColor, color: buttonTextColor }}
          >
            Get Started
          </button>
        </div>

        {/* EXPANDABLE CONTENT */}
        <div
          className={`card-nav-content absolute left-0 right-0 top-15 bottom-0 p-2 flex flex-col md:flex-row gap-2 z-10 ${
            isExpanded ? 'visible pointer-events-auto' : 'invisible pointer-events-none'
          }`}
        >
          {(items || []).slice(0, 3).map((item, idx) => (
            <div
              key={idx}
              ref={setCardRef(idx)}
              className="nav-card relative flex flex-col gap-2 p-4 rounded-lg flex-1 min-h-15"
              style={{ backgroundColor: item.bgColor, color: item.textColor }}
            >
              <div className="font-medium text-lg">{item.label}</div>
              <div className="mt-auto flex flex-col gap-2">
                {item.links?.map((lnk, i) => (
                  <a
                    key={i}
                    href={lnk.href}
                    className="flex items-center gap-2 hover:opacity-75 transition-opacity text-sm font-medium"
                  >
                    <GoArrowUpRight /> {lnk.label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default CardNav;