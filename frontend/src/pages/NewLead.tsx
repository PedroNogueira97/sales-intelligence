import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createLead } from "../api";

export default function NewLead() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const lead = await createLead({
        name,
        email,
        company_name: companyName || null,
        message,
      });
      navigate(`/leads/${lead.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  const needsCompanySetup = error?.includes("Configure a empresa");

  return (
    <section>
      <h1>Cadastrar lead</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Nome *
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Email *
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Empresa do lead
          <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
        </label>
        <label>
          Mensagem recebida *
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
            required
          />
        </label>
        {error && (
          <p className="error">
            {error} {needsCompanySetup && <Link to="/companies">Configurar empresa</Link>}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? "Salvando..." : "Salvar lead"}
        </button>
      </form>
    </section>
  );
}
