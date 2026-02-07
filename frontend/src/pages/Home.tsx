import ColorBends from "@/components/ColorBends";
import CardNav from "@/components/CardNav";

const Home = () => {
  // Mapping the Architecture Doc to CardNav items
  const navItems = [
    {
      label: "Emprunter",
      bgColor: "#590101", // Your accent color
      textColor: "#ffffff",
      links: [
        { label: "Nouvel emprunt", href: "/new-loan", ariaLabel: "Start new loan" }, // Ref 1.3
        { label: "Consulter l'inventaire", href: "/inventory", ariaLabel: "View inventory" } // Ref 1.1
      ]
    },
    {
      label: "Mon Espace",
      bgColor: "#a01801",
      textColor: "#ffffff",
      links: [
        { label: "Mes emprunts", href: "/my-loans", ariaLabel: "My loans" }, // Ref 1.2
        { label: "Mon Panier", href: "/cart", ariaLabel: "My cart" } // Ref 1.4
      ]
    },
    {
      label: "Admin",
      bgColor: "#e01b24",
      textColor: "#ffffff",
      links: [
        { label: "Gestion", href: "/admin", ariaLabel: "Management" } // Ref 1.5
      ]
    }
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Background Visuals */}
      <div className="absolute inset-0 z-0">
         <ColorBends
            colors={["#e01b24","#a51d2d", "#ffffff", "#eeaa11", "#26aaff"]}
         />
      </div>

      {/* Central Navigation Cards */}
      <div className="relative z-10 flex items-center justify-center h-full ">
        <CardNav
            // logo="/src/assets/logos/Logo CLAP.png"
            items={navItems}
            buttonBgColor="#a01806"
            baseColor="rgba(255, 255, 255, 0.1)" // Glassmorphism effect
        />
      </div>
    </div>
  );
};

export default Home;