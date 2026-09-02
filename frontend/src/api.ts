import type {
  AnalyzeResponse,
  Analysis,
  Company,
  CompanyCreate,
  CompanyUpdate,
  LandingPageLeadCreate,
  Lead,
  LeadCreate,
  LeadDetail,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail ?? `Erro ${response.status} ao chamar a API`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return response.json() as Promise<T>;
}

export function createCompany(data: CompanyCreate): Promise<Company> {
  return request<Company>("/companies", { method: "POST", body: JSON.stringify(data) });
}

export function updateCompany(data: CompanyUpdate): Promise<Company> {
  return request<Company>("/companies", { method: "PUT", body: JSON.stringify(data) });
}

/** Retorna a empresa configurada, ou `null` se ainda não houver nenhuma (404). */
export async function getCompany(): Promise<Company | null> {
  const response = await fetch(`${API_URL}/companies`, {
    headers: { "Content-Type": "application/json" },
  });
  if (response.status === 404) return null;
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Erro ${response.status} ao chamar a API`);
  }
  return response.json() as Promise<Company>;
}

export function createLead(data: LeadCreate): Promise<Lead> {
  return request<Lead>("/leads", { method: "POST", body: JSON.stringify(data) });
}

/** Simula o envio do formulário da landing page fake (SPEC.md secao 22). */
export function createLeadFromLandingPage(data: LandingPageLeadCreate): Promise<Lead> {
  return request<Lead>("/leads/landing-page", { method: "POST", body: JSON.stringify(data) });
}

export function listLeads(): Promise<LeadDetail[]> {
  return request<LeadDetail[]>("/leads");
}

export function getLead(leadId: string): Promise<LeadDetail> {
  return request<LeadDetail>(`/leads/${leadId}`);
}

/** Registra manualmente mais uma interação no histórico do lead (SPEC.md secao 8). */
export function addLeadMessage(leadId: string, content: string): Promise<LeadDetail> {
  return request<LeadDetail>(`/leads/${leadId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function analyzeLead(leadId: string): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>(`/leads/${leadId}/analyze`, { method: "POST" });
}

export function getAnalysis(leadId: string): Promise<Analysis> {
  return request<Analysis>(`/leads/${leadId}/analysis`);
}
