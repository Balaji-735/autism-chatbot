const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  question: string;
}

export interface Source {
  content: string;
  score: number;
  metadata: {
    source?: string;
    page?: number;
    id?: string;
  };
  pdf_url?: string;
  filename?: string;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export async function queryRAG(question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Backend is not healthy');
  }
  return response.json();
}

export function getPdfUrl(pdfUrl?: string): string | null {
  if (!pdfUrl) return null;
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  // If pdf_url is already absolute, return as-is, otherwise prepend API base URL
  if (pdfUrl.startsWith('http')) {
    return pdfUrl;
  }
  return `${API_BASE_URL}${pdfUrl}`;
}

