export class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function request<T>(path: string, token: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`/api${path}`, { ...options, headers, cache: 'no-store' });
  if (!response.ok) {
    let message = `Não foi possível concluir a operação (${response.status}).`;
    try { const error = await response.json(); if (typeof error.message === 'string') message = error.message; } catch { /* servidor pode não devolver JSON */ }
    if (response.status === 401) message = 'Credenciais inválidas ou sessão expirada. Entre novamente.';
    throw new ApiError(message, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
export async function download(format: 'pdf' | 'xlsx', query: string, token: string) {
  const response = await fetch(`/api/transactions/export.${format}?${query}`, {headers:{Authorization:`Bearer ${token}`}, cache:'no-store'});
  if (!response.ok) throw new ApiError('Não foi possível exportar as movimentações.', response.status);
  const url = URL.createObjectURL(await response.blob());
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = `movimentacoes.${format}`; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
