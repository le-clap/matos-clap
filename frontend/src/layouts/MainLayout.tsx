import { Outlet } from 'react-router-dom';
// import StaggeredMenu from '@/components/StaggeredMenu';
// import ColorBends from "@/components/ColorBends.tsx";
// Import other common elements like your background or User Bar here

const MainLayout = () => {

  return (

    <div className="relative min-h-screen w-full bg-[#101010]">

        {/* This is where Home, Inventory, etc. will be rendered */}
        <Outlet />
    </div>
  );
};

export default MainLayout;