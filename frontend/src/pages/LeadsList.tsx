import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { analyzeLead, listLeads } from "../api";
import type { LeadDetail } from "../types";

const STATUS_LABEL: Record<string, string> = {
  new: "Novo",
  processing: "Analisando...",
  analyzed: "Analisado",
  error: "Erro",
};

export default function LeadsList() {
  const [leads, setLeads] = useState<LeadDetail[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);

  function load() {
    listLeads()
      .then(setLeads)
      .catch((err) => setError(err.message));
  }

  useEffect(load, []);

  async function handleAnalyze(leadId: string) {
    setAnalyzingId(leadId);
    try {
      await analyzeLead(leadId);
    } catch {
      // erro é refletido no status do lead (error) após reload
    } finally {
      setAnalyzingId(null);
      load();
    }
  }

  if (error) return <p className="error">Erro ao carregar leads: {error}</p>;
  if (!leads) return <p>Carregando...</p>;

  return (
    <section>
      <h1>Leads</h1>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Empresa</th>
            <th>Score</th>
            <th>Qualificação</th>
            <th>Intenção</th>
            <th>Status</th>
            <th>Data</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>
                <Link to={`/leads/${lead.id}`}>{lead.name}</Link>
              </td>
              <td>{lead.company_name ?? "—"}</td>
              <td>{lead.analysis?.score ?? "—"}</td>
              <td>{lead.analysis?.qualification ?? "—"}</td>
              <td>{lead.analysis?.intent ?? "—"}</td>
              <td>{STATUS_LABEL[lead.status]}</td>
              <td>{new Date(lead.created_at).toLocaleDateString("pt-BR")}</td>
              <td>
                {(lead.status === "new" || lead.status === "error") && (
                  <button onClick={() => handleAnalyze(lead.id)} disabled={analyzingId === lead.id}>
                    {analyzingId === lead.id ? "Analisando..." : "Analisar"}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
