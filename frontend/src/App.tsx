import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from '@/layouts/MainLayout';
import Home from '@/pages/Home';

// Create placeholder components for pages you haven't built yetW
const Inventory = () => <div className="p-20 text-white">Page Inventaire (1.1)</div>;
const MyLoans = () => <div className="p-20 text-white">Page Mes Emprunts (1.2)</div>;
const NewLoan = () => <div className="p-20 text-white">Page Nouvel Emprunt (1.3)</div>;
const Admin = () => <div className="p-20 text-white">Page Gestion (1.5)</div>;

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Parent Route uses the Layout */}
        <Route path="/" element={<MainLayout />}>

          {/* Child Routes render inside the Layout's <Outlet /> */}
          <Route index element={<Home />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="my-loans" element={<MyLoans />} />
          <Route path="new-loan" element={<NewLoan />} />
          <Route path="admin" element={<Admin />} />

          {/* Fallback for 404 */}
          <Route path="*" element={<div className="text-white">404 - Not Found</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;