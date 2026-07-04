import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { RequireAuth, RequireRole } from "@/components/RouteGuards";
import { CartProvider } from "@/features/cart/CartContext";
import { AppLayout } from "@/layouts/AppLayout";
import { AdminLayout } from "@/layouts/AdminLayout";

import { LoginPage } from "@/pages/Login";
import { NotFound } from "@/pages/NotFound";
import { CatalogPage } from "@/pages/Catalog";
import { CatalogDetailPage } from "@/pages/CatalogDetail";
import { RequestBuilderPage } from "@/pages/RequestBuilder";
import { MyRequestsPage } from "@/pages/MyRequests";
import { MyLoansPage } from "@/pages/MyLoans";

import { DashboardPage } from "@/pages/admin/Dashboard";
import { AdminRequestsPage } from "@/pages/admin/Requests";
import { AdminRequestDetailPage } from "@/pages/admin/RequestDetail";
import { AdminLoansPage } from "@/pages/admin/Loans";
import { AdminLoanDetailPage } from "@/pages/admin/LoanDetail";
import { AdminNewLoanPage } from "@/pages/admin/NewLoan";
import { AdminTimelinePage } from "@/pages/admin/Timeline";
import { AdminInventoryPage } from "@/pages/admin/Inventory";
import { AdminUsersPage } from "@/pages/admin/Users";

function HomeRedirect() {
  const { hasRole } = useAuth();
  return <Navigate to={hasRole("clap") ? "/admin" : "/catalog"} replace />;
}

export function App() {
  return (
    <CartProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* User-facing app */}
        <Route
          element={
            <RequireAuth>
              <AppLayout />
            </RequireAuth>
          }
        >
          <Route index element={<HomeRedirect />} />
          <Route path="/catalog" element={<CatalogPage />} />
          <Route path="/catalog/:id" element={<CatalogDetailPage />} />
          <Route path="/request" element={<RequestBuilderPage />} />
          <Route path="/my/requests" element={<MyRequestsPage />} />
          <Route path="/my/loans" element={<MyLoansPage />} />
        </Route>

        {/* Backoffice */}
        <Route
          path="/admin"
          element={
            <RequireAuth>
              <RequireRole min="clap">
                <AdminLayout />
              </RequireRole>
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="requests" element={<AdminRequestsPage />} />
          <Route path="requests/:id" element={<AdminRequestDetailPage />} />
          <Route path="planning" element={<AdminTimelinePage />} />
          <Route path="loans" element={<AdminLoansPage />} />
          <Route path="loans/new" element={<AdminNewLoanPage />} />
          <Route path="loans/:id" element={<AdminLoanDetailPage />} />
          <Route
            path="inventory"
            element={
              <RequireRole min="manager">
                <AdminInventoryPage />
              </RequireRole>
            }
          />
          <Route path="users" element={<AdminUsersPage />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </CartProvider>
  );
}
