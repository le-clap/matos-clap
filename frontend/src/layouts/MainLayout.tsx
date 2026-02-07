import { Outlet } from 'react-router-dom';
import StaggeredMenu from '@/components/StaggeredMenu';
// import ColorBends from "@/components/ColorBends.tsx";
// Import other common elements like your background or User Bar here

const MainLayout = () => {
  // Your existing menu items configuration
  const menuItems = [
    { label: 'Accueil', link: '/' },
    { label: 'Inventaire', link: '/inventory' },
    { label: 'Mes Emprunts', link: '/my-loans' },
    { label: 'Panier', link: '/cart' },
  ];

  const socialItems = [
  { label: 'Instagram', link: 'https://www.instagram.com/le_clap_/' },
  { label: 'GitHub', link: 'https://github.com/le-clap' }
  ];

  return (
    <div className="relative min-h-screen w-full bg-[#101010]">
        <StaggeredMenu
            position="right"
            isFixed={true}
            items={menuItems}
            socialItems={socialItems}
            displayItemNumbering={true}
            menuButtonColor="#aaffff"
            openMenuButtonColor="#000"
            changeMenuColorOnOpen={true}
            colors={['#f01801', '#262626']}
            logoUrl="/src/assets/logos/Logo CLAP.png"
            accentColor='#f01802'
            onMenuOpen={() => console.log('Menu opened')}
            onMenuClose={() => console.log('Menu closed')}
        />

        {/* This is where Home, Inventory, etc. will be rendered */}
        <Outlet />
    </div>
  );
};

export default MainLayout;