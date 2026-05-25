import {Outlet, useNavigate} from 'react-router-dom';
import Footer from "@/components/Footer";

// import CardNav from "@/components/ui/CardNav";
import NavMenu, {type NavMenuItem} from "@/components/NavMenu.tsx";

import {ModeToggle} from "@/components/ModeToggle";
import clapLogo from "@/assets/logos/Logo CLAP.png";

import LoginButton from "@/components/LoginButton.tsx";

const MainLayout = () => {

  const navItems: NavMenuItem[] = [
    {
      label: "Emprunter",
      links: [
        {label: "Nouvel emprunt", desc:'Lorem ispum', href: "/new-loan", ariaLabel: "Start new loan"}, // Ref 1.3
        {label: "Consulter l'inventaire", desc:'Lorem ispum', href: "/inventory", ariaLabel: "View inventory"} // Ref 1.1
      ]
    },
    {
      label: "Mon Espace",
      links: [
        {label: "Mes emprunts", desc:'Lorem ispum', href: "/my-loans", ariaLabel: "My loans"}, // Ref 1.2
        {label: "Mon Panier", desc:'Lorem ispum', href: "/cart", ariaLabel: "My cart"} // Ref 1.4
      ]
    },
    {
      label: "Admin",
      links: [
        {label: "Gestion", desc:'Lorem ispum', href: "/admin", ariaLabel: "Management"} // Ref 1.5
      ]
    }
  ];
  const navigate = useNavigate();

  return (

    // Flex container to manage full height
    <div className="flex flex-col min-h-screen w-full bg-background text-foreground">

      <div className="fixed z-3 flex gap-3 p-3 px-3 justify-between w-full border-foreground border-b bg-transparent backdrop-blur-xl">
        <div className="left-menu flex">
          <div className="flex items-center gap-3">
            <a onClick={(e) => {
              e.preventDefault();
              navigate('/');
            }} href='/'>
              <img src={clapLogo} alt="Logo CLAP" className="h-10 w-auto"/>
            </a>
            <div className="h-6 w-0.5 rounded-full bg-foreground "></div>
          </div>
          <NavMenu items={navItems} className={'pl-1'}></NavMenu>
        </div>

        <div className="right-buttons flex gap-3">
          <div className="">
            <LoginButton/>
          </div>
          <div>
            <ModeToggle/>
          </div>
        </div>
      </div>

      {/* Central Navigation Card */}
      {/*<div className="relative z-10 flex items-center justify-center h-full">*/}
      {/*  <CardNav*/}
      {/*    // logo="/src/assets/logos/Logo CLAP.png"*/}
      {/*    items={navItems}*/}
      {/*    buttonBgColor="#a01801"*/}
      {/*    menuColor="#a01801"*/}
      {/*    centerText="CLAP"*/}
      {/*    baseColor="var(--nav-bg)"*/}
      {/*  />*/}
      {/*</div>*/}

      {/* Main Content Area */}
      {/* flex-grow ensures this takes all available space, pushing Footer down */}
      <main className="grow w-full relative z-1">
        {/* The Outlet renders the current page (Home, Inventory, etc.) */}
        <Outlet/>
      </main>

      {/* Footer stays at the bottom */}
      <Footer/>
    </div>
  );
};

export default MainLayout;
