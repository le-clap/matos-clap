import {Outlet} from 'react-router-dom';
import Footer from "@/components/Footer.tsx";
import CardNav from "@/components/CardNav.tsx";

const MainLayout = () => {

  const navItems = [
    {
      label: "Emprunter",
      bgColor: "#590101", // Your accent color
      textColor: "#ffffff",
      links: [
        {label: "Nouvel emprunt", href: "/new-loan", ariaLabel: "Start new loan"}, // Ref 1.3
        {label: "Consulter l'inventaire", href: "/inventory", ariaLabel: "View inventory"} // Ref 1.1
      ]
    },
    {
      label: "Mon Espace",
      bgColor: "#a01801",
      textColor: "#ffffff",
      links: [
        {label: "Mes emprunts", href: "/my-loans", ariaLabel: "My loans"}, // Ref 1.2
        {label: "Mon Panier", href: "/cart", ariaLabel: "My cart"} // Ref 1.4
      ]
    },
    {
      label: "Admin",
      bgColor: "#e01b24",
      textColor: "#ffffff",
      links: [
        {label: "Gestion", href: "/admin", ariaLabel: "Management"} // Ref 1.5
      ]
    }
  ];

  return (

    // Flex container to manage full height
    <div className="flex flex-col min-h-screen w-full bg-[#101010] text-white">

      {/* Central Navigation Card */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <CardNav
          // logo="/src/assets/logos/Logo CLAP.png"
          items={navItems}
          buttonBgColor="#a01806"
          menuColor="#a01806"
          baseColor="rgba(255, 255, 255, 0.1)" // Glassmorphism effect
        />
      </div>

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