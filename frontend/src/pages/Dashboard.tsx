import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCompany, listLeads } from "../api";
import type { Company, LeadDetail } from "../types";

export default function Dashboard() {
  const [leads, setLeads] = useState<LeadDetail[] | null>(null);
  const [company, setCompany] = useState<Company | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listLeads()
      .then(setLeads)
      .catch((err) => setError(err.message));
    getCompany()
      .then(setCompany)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="error">Erro ao carregar dashboard: {error}</p>;
  if (!leads || company === undefined) return <p>Carregando...</p>;

  if (company === null) {
    return (
      <section>
        <h1>Dashboard</h1>
        <p>
          Configure sua empresa antes de cadastrar leads — é esse contexto (produto, ICP, dores,
          tom) que a análise usa para qualificar cada lead que chegar.
        </p>
        <div className="actions">
          <Link className="button" to="/companies">
            Configurar empresa
          </Link>
        </div>
      </section>
    );
  }

  const total = leads.length;
  const analyzed = leads.filter((l) => l.status === "analyzed").length;
  const qualified = leads.filter((l) => l.analysis?.qualification === "qualified").length;
  const awaiting = leads.filter((l) => l.status === "new").length;

  return (
    <section>
      <h1>Dashboard</h1>
      <div className="cards">
        <div className="card">
          <span className="card-value">{total}</span>
          <span className="card-label">Total de leads</span>
        </div>
        <div className="card">
          <span className="card-value">{analyzed}</span>
          <span className="card-label">Leads analisados</span>
        </div>
        <div className="card">
          <span className="card-value">{qualified}</span>
          <span className="card-label">Leads qualificados</span>
        </div>
        <div className="card">
          <span className="card-value">{awaiting}</span>
          <span className="card-label">Aguardando análise</span>
        </div>
      </div>
      <div className="actions">
        <Link className="button" to="/leads/new">
          Cadastrar lead
        </Link>
        <Link className="button" to="/leads">
          Ver leads
        </Link>
      </div>
    </section>
  );
}
