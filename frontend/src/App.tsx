import { BrowserRouter, Link, Outlet, Route, Routes } from "react-router-dom";
import CompanySettings from "./pages/CompanySettings";
import Dashboard from "./pages/Dashboard";
import FakeLandingPage from "./pages/FakeLandingPage";
import LeadDetail from "./pages/LeadDetail";
import LeadsList from "./pages/LeadsList";
import NewLead from "./pages/NewLead";

function DashboardLayout() {
  return (
    <>
      <header className="topbar">
        <Link to="/" className="brand">
          Sales Intelligence
        </Link>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/leads">Leads</Link>
          <Link to="/leads/new">Novo lead</Link>
          <Link to="/companies">Empresa</Link>
          <a href="/lp" target="_blank" rel="noreferrer">
            Landing page ↗
          </a>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rota pública, sem o layout do dashboard interno — simula um site externo (SPEC.md secao 22) */}
        <Route path="/lp" element={<FakeLandingPage />} />

        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/companies" element={<CompanySettings />} />
          <Route path="/leads" element={<LeadsList />} />
          <Route path="/leads/new" element={<NewLead />} />
          <Route path="/leads/:leadId" element={<LeadDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
