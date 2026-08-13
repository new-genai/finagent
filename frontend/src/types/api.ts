export interface DatasetStatsResponse {
  total_files: number;
  total_tables: number;
  companies: string[];
  years: string[];
}

export interface RetrieveRequest {
  question: string;
}

export interface RetrievedTable {
  table_id: string;
  company: string;
  year: string;
  score: number;
  preview: string[][];
}

export interface RetrieveResponse {
  tables: RetrievedTable[];
}

export interface ExecuteRequest {
  code: string;
}

export interface ExecuteResponse {
  success: boolean;
  result?: string;
  error?: string;
}

export interface ChatRequest {
  question: string;
  history?: Array<{ role: 'user' | 'assistant'; content: string }>;
}

export interface ChatResponse {
  answer: string;
  thought_process?: string;
  tables_used: string[];
}
