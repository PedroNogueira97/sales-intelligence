import { useState } from "react";
import { Link } from "react-router-dom";
import { createCompany } from "../api";
import type { Company } from "../types";

export default function NewCompany() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [idealCustomerProfile, setIdealCustomerProfile] = useState("");
  const [averageTicket, setAverageTicket] = useState("");
  const [painPoints, setPainPoints] = useState("");
  const [communicationTone, setCommunicationTone] = useState("");
  const [created, setCreated] = useState<Company | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const company = await createCompany({
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
      });
      setCreated(company);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (created) {
    return (
      <section>
        <h1>Empresa criada</h1>
        <p>
          <strong>{created.name}</strong> foi cadastrada com sucesso. Copie o ID abaixo para
          cadastrar leads para esta empresa:
        </p>
        <code className="id-box">{created.id}</code>
        <div className="actions">
          <Link className="button" to="/leads/new">
            Cadastrar lead
          </Link>
          <Link className="button" to="/">
            Voltar ao dashboard
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section>
      <h1>Cadastrar empresa</h1>
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
        <button type="submit" disabled={submitting}>
          {submitting ? "Salvando..." : "Salvar empresa"}
        </button>
      </form>
    </section>
  );
}
