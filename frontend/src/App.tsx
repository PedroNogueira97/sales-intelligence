import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import CompanySettings from "./pages/CompanySettings";
import Dashboard from "./pages/Dashboard";
import LeadDetail from "./pages/LeadDetail";
import LeadsList from "./pages/LeadsList";
import NewLead from "./pages/NewLead";

export default function App() {
  return (
    <BrowserRouter>
      <header className="topbar">
        <Link to="/" className="brand">
          Sales Intelligence
        </Link>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/leads">Leads</Link>
          <Link to="/leads/new">Novo lead</Link>
          <Link to="/companies">Empresa</Link>
        </nav>
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/companies" element={<CompanySettings />} />
          <Route path="/leads" element={<LeadsList />} />
          <Route path="/leads/new" element={<NewLead />} />
          <Route path="/leads/:leadId" element={<LeadDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
