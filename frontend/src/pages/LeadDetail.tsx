import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { analyzeLead, getLead } from "../api";
import type { LeadDetail as LeadDetailType } from "../types";

const RECOMMENDED_ACTION_LABEL: Record<string, string> = {
  schedule_demo: "Agendar demonstração",
  contact_salesperson: "Contatar vendedor",
  ask_more_information: "Pedir mais informações",
  nurturing: "Nutrir lead",
  discard: "Descartar",
};

const CHANNEL_LABEL: Record<string, string> = {
  manual: "Manual",
  whatsapp: "WhatsApp",
  landing_page: "Landing page",
};

const RESPONSE_FORMAT_LABEL: Record<string, string> = {
  whatsapp: "WhatsApp",
  manual: "Email",
  landing_page: "Email",
};

export default function LeadDetail() {
  const { leadId } = useParams<{ leadId: string }>();
  const [lead, setLead] = useState<LeadDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [editedResponse, setEditedResponse] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copiedScript, setCopiedScript] = useState(false);

  function load() {
    if (!leadId) return;
    getLead(leadId)
      .then((data) => {
        setLead(data);
        setEditedResponse(data.analysis?.response ?? "");
      })
      .catch((err) => setError(err.message));
  }

  useEffect(load, [leadId]);

  async function handleAnalyze() {
    if (!leadId) return;
    setAnalyzing(true);
    setError(null);
    try {
      await analyzeLead(leadId);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setAnalyzing(false);
      load();
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(editedResponse);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Não foi possível copiar automaticamente. Selecione o texto manualmente.");
    }
  }

  async function handleCopyScript() {
    if (!lead?.analysis?.call_script) return;
    try {
      await navigator.clipboard.writeText(lead.analysis.call_script);
      setCopiedScript(true);
      setTimeout(() => setCopiedScript(false), 2000);
    } catch {
      setError("Não foi possível copiar automaticamente. Selecione o texto manualmente.");
    }
  }

  if (error && !lead) return <p className="error">Erro ao carregar lead: {error}</p>;
  if (!lead) return <p>Carregando...</p>;

  const { analysis } = lead;

  return (
    <section>
      <h1>{lead.name}</h1>
      <dl className="lead-info">
        <dt>Empresa</dt>
        <dd>{lead.company_name ?? "não informado"}</dd>
        <dt>Canal</dt>
        <dd>{CHANNEL_LABEL[lead.channel]}</dd>
        {lead.email && (
          <>
            <dt>Email</dt>
            <dd>{lead.email}</dd>
          </>
        )}
        {lead.phone && (
          <>
            <dt>Telefone</dt>
            <dd>{lead.phone}</dd>
          </>
        )}
        <dt>Mensagem original</dt>
        <dd>{lead.message}</dd>
      </dl>

      {error && <p className="error">{error}</p>}

      {(lead.status === "new" || lead.status === "error") && (
        <button onClick={handleAnalyze} disabled={analyzing}>
          {analyzing ? "Analisando..." : "Executar análise"}
        </button>
      )}
      {lead.status === "processing" && <p>Análise em andamento...</p>}
      {lead.status === "error" && <p className="error">A última análise falhou. Tente novamente.</p>}

      {analysis && (
        <>
          <div className="block">
            <h2>ANÁLISE</h2>
            <p>Score: {analysis.score}</p>
            <p>Qualificação: {analysis.qualification.toUpperCase()}</p>
            <p>Intenção: {analysis.intent.toUpperCase()}</p>
            <p>Confiança: {Math.round(analysis.confidence * 100)}%</p>
          </div>

          <div className="block">
            <h2>POR QUE?</h2>
            <ul>
              {analysis.reasons.map((reason, i) => (
                <li key={i}>✓ {reason}</li>
              ))}
            </ul>
          </div>

          <div className="block">
            <h2>DORES</h2>
            {analysis.pain_points.length === 0 ? (
              <p>Nenhuma dor identificada.</p>
            ) : (
              <ul>
                {analysis.pain_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="block">
            <h2>PRÓXIMA AÇÃO</h2>
            <p>{RECOMMENDED_ACTION_LABEL[analysis.recommended_action]}</p>
          </div>

          <div className="block">
            <h2>RESPOSTA SUGERIDA ({RESPONSE_FORMAT_LABEL[lead.channel]})</h2>
            {isEditing ? (
              <textarea
                value={editedResponse}
                onChange={(e) => setEditedResponse(e.target.value)}
                rows={8}
              />
            ) : (
              <p className="response-text">{editedResponse}</p>
            )}
            <div className="actions">
              <button onClick={() => setIsEditing((v) => !v)}>
                {isEditing ? "Concluir edição" : "Editar"}
              </button>
              <button onClick={handleCopy}>{copied ? "Copiado!" : "Copiar"}</button>
            </div>
          </div>

          {analysis.call_script && (
            <div className="block">
              <h2>ROTEIRO PARA LIGAÇÃO</h2>
              <p className="response-text">{analysis.call_script}</p>
              <div className="actions">
                <button onClick={handleCopyScript}>{copiedScript ? "Copiado!" : "Copiar"}</button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
