import type {
  AnalyzeResponse,
  Analysis,
  Company,
  CompanyCreate,
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

export function getCompany(companyId: string): Promise<Company> {
  return request<Company>(`/companies/${companyId}`);
}

export function createLead(data: LeadCreate): Promise<Lead> {
  return request<Lead>("/leads", { method: "POST", body: JSON.stringify(data) });
}

export function listLeads(): Promise<LeadDetail[]> {
  return request<LeadDetail[]>("/leads");
}

export function getLead(leadId: string): Promise<LeadDetail> {
  return request<LeadDetail>(`/leads/${leadId}`);
}

export function analyzeLead(leadId: string): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>(`/leads/${leadId}/analyze`, { method: "POST" });
}

export function getAnalysis(leadId: string): Promise<Analysis> {
  return request<Analysis>(`/leads/${leadId}/analysis`);
}
