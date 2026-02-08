import {BrowserRouter, Routes, Route} from 'react-router-dom';
import MainLayout from '@/layouts/MainLayout';
import Home from '@/pages/Home';
import Inventory from '@/pages/Inventory';
import MyLoans from "@/pages/MyLoans.tsx";
import NewLoan from "@/pages/NewLoan.tsx";
import Cart from "@/pages/Cart";

import Error from "@/pages/Error";

// Create placeholder components for pages you haven't built yet

const Admin = () => <div className="p-20 min-h-screen text-white">Page Gestion (1.5)</div>;

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Parent Route uses the Layout */}
        <Route path="/" element={<MainLayout/>}>

          {/* Child Routes render inside the Layout's <Outlet /> */}
          <Route index element={<Home/>}/>
          <Route path="inventory" element={<Inventory/>}/>
          <Route path="my-loans" element={<MyLoans/>}/>
          <Route path="new-loan" element={<NewLoan/>}/>
          <Route path="cart" element={<Cart/>}/>
          <Route path="admin" element={<Admin/>}/>

          {/* Fallback for 404 */}
          <Route path="*" element={<Error/>}/>
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;