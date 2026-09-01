import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createCompany, getCompany, updateCompany } from "../api";
import type { Company } from "../types";

export default function CompanySettings() {
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [idealCustomerProfile, setIdealCustomerProfile] = useState("");
  const [averageTicket, setAverageTicket] = useState("");
  const [painPoints, setPainPoints] = useState("");
  const [communicationTone, setCommunicationTone] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [justCreated, setJustCreated] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  function fillForm(data: Company) {
    setName(data.name);
    setDescription(data.description ?? "");
    setProductDescription(data.product_description ?? "");
    setIdealCustomerProfile(data.ideal_customer_profile ?? "");
    setAverageTicket(data.average_ticket?.toString() ?? "");
    setPainPoints(data.pain_points.join(", "));
    setCommunicationTone(data.communication_tone ?? "");
  }

  useEffect(() => {
    getCompany()
      .then((data) => {
        setCompany(data);
        if (data) fillForm(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSubmitting(true);
    const payload = {
      name,
      description: description || null,
      product_description: productDescription || null,
      ideal_customer_profile: idealCustomerProfile || null,
      average_ticket: averageTicket ? Number(averageTicket) : null,
      pain_points: painPoints
        .split(",")
        .map((p) => p.trim())
        .filter(Boolean),
      communication_tone: communicationTone || null,
    };
    try {
      const wasCreate = company === null;
      const result = wasCreate ? await createCompany(payload) : await updateCompany(payload);
      setCompany(result);
      setSaved(true);
      setJustCreated(wasCreate);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p>Carregando...</p>;

  return (
    <section>
      <h1>Empresa</h1>
      <p>
        Este é o contexto comercial usado para analisar todos os leads: produto, perfil de
        cliente ideal, dores e tom de comunicação. Configurado uma única vez por instalação.
      </p>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Nome *
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Descrição
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
        </label>
        <label>
          Produto/serviço
          <textarea
            value={productDescription}
            onChange={(e) => setProductDescription(e.target.value)}
          />
        </label>
        <label>
          Perfil de cliente ideal (ICP)
          <textarea
            value={idealCustomerProfile}
            onChange={(e) => setIdealCustomerProfile(e.target.value)}
          />
        </label>
        <label>
          Ticket médio
          <input
            type="number"
            min="0"
            value={averageTicket}
            onChange={(e) => setAverageTicket(e.target.value)}
          />
        </label>
        <label>
          Principais dores que resolve (separadas por vírgula)
          <input value={painPoints} onChange={(e) => setPainPoints(e.target.value)} />
        </label>
        <label>
          Tom de comunicação
          <input
            value={communicationTone}
            onChange={(e) => setCommunicationTone(e.target.value)}
            placeholder="professional"
          />
        </label>
        {error && <p className="error">{error}</p>}
        {saved && <p>Empresa salva.</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Salvando..." : company ? "Salvar alterações" : "Salvar empresa"}
        </button>
      </form>
      {saved && justCreated && (
        <div className="actions">
          <Link className="button" to="/leads/new">
            Cadastrar lead
          </Link>
        </div>
      )}
    </section>
  );
}
