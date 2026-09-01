import { useState } from "react";
import { createLeadFromLandingPage } from "../api";

export default function FakeLandingPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createLeadFromLandingPage({
        name,
        email,
        phone: phone || null,
        message,
      });
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="content" style={{ maxWidth: 560, margin: "0 auto" }}>
      <section>
        <h1>Acme Sales — Automatize seu funil comercial</h1>
        <p>
          Pare de perder leads em planilhas. Fale com a gente e veja como a Acme Sales pode
          ajudar sua equipe comercial.
        </p>

        {submitted ? (
          <p>Obrigado! Entraremos em contato em breve.</p>
        ) : (
          <form onSubmit={handleSubmit} className="form">
            <label>
              Nome *
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              Email *
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>
            <label>
              Telefone
              <input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </label>
            <label>
              Como podemos ajudar? *
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={4}
                required
              />
            </label>
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={submitting}>
              {submitting ? "Enviando..." : "Quero saber mais"}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}
