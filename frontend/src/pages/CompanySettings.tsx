import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createCompany, getCompany, updateCompany } from "../api";
import type { Company, Product } from "../types";

export default function CompanySettings() {
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
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
    setProducts(data.products);
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

  function addProduct() {
    setProducts((prev) => [...prev, { name: "", description: "" }]);
  }

  function removeProduct(index: number) {
    setProducts((prev) => prev.filter((_, i) => i !== index));
  }

  function updateProduct(index: number, field: keyof Product, value: string) {
    setProducts((prev) =>
      prev.map((product, i) => (i === index ? { ...product, [field]: value } : product))
    );
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSaved(false);
    setSubmitting(true);
    const payload = {
      name,
      description: description || null,
      product_description: productDescription || null,
      products: products
        .filter((p) => p.name.trim())
        .map((p) => ({ name: p.name.trim(), description: p.description?.trim() || null })),
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
      setProducts(result.products);
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
        Este é o contexto comercial usado para analisar todos os leads: produtos, perfil de
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
          Resumo geral do produto/serviço
          <textarea
            value={productDescription}
            onChange={(e) => setProductDescription(e.target.value)}
          />
        </label>

        <div>
          <span className="form-section-label">Produtos/serviços</span>
          {products.map((product, index) => (
            <div className="product-row" key={index}>
              <input
                value={product.name}
                onChange={(e) => updateProduct(index, "name", e.target.value)}
                placeholder="Nome do produto"
              />
              <input
                value={product.description ?? ""}
                onChange={(e) => updateProduct(index, "description", e.target.value)}
                placeholder="Descrição (opcional)"
              />
              <button type="button" onClick={() => removeProduct(index)}>
                Remover
              </button>
            </div>
          ))}
          <button type="button" onClick={addProduct}>
            + Adicionar produto
          </button>
        </div>

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
