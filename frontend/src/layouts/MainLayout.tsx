import { Outlet } from 'react-router-dom';
import Footer from "@/components/Footer.tsx";

const MainLayout = () => {

  return (

    // Flex container to manage full height
    <div className="flex flex-col min-h-screen w-full bg-[#101010] text-white">

        {/* Main Content Area */}
        {/* flex-grow ensures this takes all available space, pushing Footer down */}
        <main className="grow w-full relative z-10">
            {/* The Outlet renders the current page (Home, Inventory, etc.) */}
            <Outlet />
        </main>

        {/* Footer stays at the bottom */}
        <Footer />
    </div>
  );
};

export default MainLayout;