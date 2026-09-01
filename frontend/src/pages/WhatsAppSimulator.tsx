import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createLeadFromWhatsapp } from "../api";

export default function WhatsAppSimulator() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const lead = await createLeadFromWhatsapp({ name, phone, message });
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
      <h1>Simular mensagem do WhatsApp</h1>
      <p>
        Não é uma integração real com o WhatsApp — só uma forma conveniente de gerar um lead
        marcado como vindo desse canal, para testar a análise sem precisar de uma conta/API real
        (ver <code>SPEC.md</code>, seção 23).
      </p>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Nome *
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Telefone *
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+5511999999999"
            required
          />
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
          {submitting ? "Enviando..." : "Simular envio"}
        </button>
      </form>
    </section>
  );
}
