export type LeadStatus = "new" | "processing" | "analyzed" | "error";
export type Qualification = "qualified" | "maybe" | "unqualified";
export type Intent = "high" | "medium" | "low" | "unknown";
export type RecommendedAction =
  | "schedule_demo"
  | "contact_salesperson"
  | "ask_more_information"
  | "nurturing"
  | "discard";

export interface Company {
  id: string;
  name: string;
  description: string | null;
  product_description: string | null;
  ideal_customer_profile: string | null;
  average_ticket: number | null;
  pain_points: string[];
  communication_tone: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
  description?: string | null;
  product_description?: string | null;
  ideal_customer_profile?: string | null;
  average_ticket?: number | null;
  pain_points?: string[];
  communication_tone?: string | null;
}

export interface CompanyUpdate {
  name?: string;
  description?: string | null;
  product_description?: string | null;
  ideal_customer_profile?: string | null;
  average_ticket?: number | null;
  pain_points?: string[];
  communication_tone?: string | null;
}

export interface Analysis {
  id: string;
  lead_id: string;
  score: number;
  qualification: Qualification;
  intent: Intent;
  confidence: number;
  pain_points: string[];
  reasons: string[];
  recommended_action: RecommendedAction;
  response: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  company_id: string;
  name: string;
  email: string;
  company_name: string | null;
  message: string;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
}

export interface LeadDetail extends Lead {
  analysis: Analysis | null;
}

export interface LeadCreate {
  name: string;
  email: string;
  company_name?: string | null;
  message: string;
}

export interface AnalyzeResponse {
  lead_id: string;
  status: string;
}
