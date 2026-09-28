export const API_BASE = (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000'))
  ? `${window.location.protocol}//${window.location.hostname}:8000/api`
  : '/api';

async function fetcher(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `API Error: ${res.statusText}`);
  }
  return res.json();
}

export const fetchDrugs = (coreOnly = true) => fetcher(coreOnly ? '/drugs?core_only=true' : '/drugs');
export const fetchDrug = (id: string) => fetcher(`/drugs/${id}`);
export const createDrug = (data: any) => fetcher('/drugs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const validateDrug = (data: any) => fetcher('/drugs/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const deleteDrug = (id: string) => fetcher(`/drugs/${id}`, { method: 'DELETE' });

export const fetchPolymers = (coreOnly = true) => fetcher(coreOnly ? '/polymers?core_only=true' : '/polymers');
export const fetchPolymer = (id: string) => fetcher(`/polymers/${id}`);
export const createPolymer = (data: any) => fetcher('/polymers', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const validatePolymer = (data: any) => fetcher('/polymers/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const deletePolymer = (id: string) => fetcher(`/polymers/${id}`, { method: 'DELETE' });

export const runScreening = (data: any) => fetcher('/screening/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
export const fetchScreeningResult = (id: string) => fetcher(`/screening/${id}`);
export const fetchHistory = () => fetcher('/history');
export const deleteHistory = (id: string) => fetcher(`/history/${id}`, { method: 'DELETE' });
export const fetchVersion = () => fetcher('/version');

export const getFigureUrl = (analysisId: string, figureName: string) => `${API_BASE}/screening/${analysisId}/figures/${figureName}`;
export const getReportUrl = (analysisId: string, filename: string) => `${API_BASE}/screening/${analysisId}/reports/${filename}`;
export const getFullReportUrl = (analysisId: string) => `${API_BASE}/screening/${analysisId}/export-full-report`;

