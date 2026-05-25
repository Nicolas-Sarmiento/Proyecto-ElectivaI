/**
 * Servicio API — conecta el frontend con el backend Flask.
 * Gestiona autenticación con tokens JWT en localStorage.
 */

const API_BASE = "http://localhost:5000/api";

// ─── Auth helpers ────────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

export function getRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}

export function saveTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

// ─── Fetch wrapper con auth ──────────────────────────────────────────────────

async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // No poner Content-Type si es FormData (el browser lo pone con boundary)
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // Si el token expiró, intentar refresh
  if (resp.status === 401 && getRefreshToken()) {
    const refreshed = await refreshTokens();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${getAccessToken()}`;
      return fetch(`${API_BASE}${path}`, { ...options, headers });
    } else {
      clearTokens();
      window.location.reload();
    }
  }

  return resp;
}

// ─── Auth endpoints ──────────────────────────────────────────────────────────

export async function login(
  username: string,
  password: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const resp = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await resp.json();

    if (resp.ok) {
      saveTokens(data.access_token, data.refresh_token);
      return { success: true };
    }
    return { success: false, error: data.error || "Error de autenticación" };
  } catch {
    return { success: false, error: "No se pudo conectar con el servidor" };
  }
}

export async function registerUser(
  data: { username: string; password: string; email?: string; first_name?: string; last_name?: string }
): Promise<{ success: boolean; error?: string }> {
  try {
    const resp = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const resData = await resp.json();

    if (resp.ok) {
      return { success: true };
    }
    return { success: false, error: resData.error || "Error de registro" };
  } catch {
    return { success: false, error: "No se pudo conectar con el servidor" };
  }
}

export async function logout(): Promise<void> {
  const refresh = getRefreshToken();
  if (refresh) {
    try {
      await apiFetch("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refresh }),
      });
    } catch { /* ignore */ }
  }
  clearTokens();
}

async function refreshTokens(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  try {
    const resp = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (resp.ok) {
      const data = await resp.json();
      saveTokens(data.access_token, data.refresh_token);
      return true;
    }
  } catch { /* ignore */ }

  return false;
}

export async function getMe(): Promise<any> {
  const resp = await apiFetch("/auth/me");
  if (resp.ok) return resp.json();
  return null;
}

// ─── Tipos ───────────────────────────────────────────────────────────────────

export interface Publication {
  publication_id: string;
  title: string;
  publish_date: string | null;
  resource_url: string | null;
  keywords: string[];
  publication_type: { type_id: string; type_name: string } | null;
  authors: Author[];
  // Campos de búsqueda semántica
  similarity?: number;
  matched_text?: string;
  matched_page?: number;
}

export interface Author {
  author_id: string;
  first_name: string;
  last_name: string;
  orcid_url: string | null;
  country: string | null;
  organization: { organization_id: string; name: string } | null;
}

export interface PublicationType {
  type_id: string;
  type_name: string;
}

// ─── Publications ────────────────────────────────────────────────────────────

export async function getPublications(keyword?: string): Promise<Publication[]> {
  const params = keyword 
    ? `?${keyword.split(',').map(k => `keyword=${encodeURIComponent(k.trim())}`).filter(k => k !== 'keyword=').join('&')}` 
    : "";
  const resp = await apiFetch(`/publications${params}`);
  if (resp.ok) return resp.json();
  return [];
}

export async function getPublicationsByAuthor(authorId: string): Promise<Publication[]> {
  const resp = await apiFetch(`/publications?author_id=${authorId}`);
  if (resp.ok) return resp.json();
  return [];
}

export async function getPublication(id: string): Promise<Publication | null> {
  const resp = await apiFetch(`/publications/${id}`);
  if (resp.ok) return resp.json();
  return null;
}

export async function createPublication(formData: FormData): Promise<{ ok: boolean; data?: Publication; error?: string }> {
  try {
    const resp = await apiFetch("/publications", {
      method: "POST",
      body: formData,
    });
    
    if (resp.status === 413) {
      return { ok: false, error: "El archivo es demasiado grande. El límite es 100 MB." };
    }

    const data = await resp.json();
    if (resp.ok) return { ok: true, data };
    return { ok: false, error: data.error || "Error al crear la publicación" };
  } catch (e) {
    return { ok: false, error: "Ocurrió un error inesperado al enviar el archivo." };
  }
}

export async function updatePublication(id: string, formData: FormData): Promise<{ ok: boolean; data?: Publication; error?: string }> {
  try {
    const resp = await apiFetch(`/publications/${id}`, {
      method: "PUT",
      body: formData,
    });
    
    if (resp.status === 413) {
      return { ok: false, error: "El archivo es demasiado grande. El límite es 100 MB." };
    }

    const data = await resp.json();
    if (resp.ok) return { ok: true, data };
    return { ok: false, error: data.error || "Error al actualizar" };
  } catch (e) {
    return { ok: false, error: "Ocurrió un error inesperado al enviar el archivo." };
  }
}

export async function deletePublication(id: string): Promise<boolean> {
  const resp = await apiFetch(`/publications/${id}`, { method: "DELETE" });
  return resp.ok;
}

export function getFileDownloadUrl(pubId: string): string {
  return `${API_BASE}/publications/${pubId}/file`;
}

// ─── Búsqueda Semántica ──────────────────────────────────────────────────────

export async function semanticSearch(query: string, limit = 10): Promise<Publication[]> {
  const params = `?q=${encodeURIComponent(query)}&limit=${limit}`;
  const resp = await apiFetch(`/search${params}`);
  if (resp.ok) return resp.json();
  return [];
}

// ─── Authors ─────────────────────────────────────────────────────────────────

export async function getAuthors(): Promise<Author[]> {
  const resp = await apiFetch("/authors");
  if (resp.ok) return resp.json();
  return [];
}

export async function createAuthor(data: { first_name: string; last_name: string; country?: string; orcid_url?: string; organization_id?: string }): Promise<{ ok: boolean; data?: Author; error?: string }> {
  const resp = await apiFetch("/authors", {
    method: "POST",
    body: JSON.stringify(data)
  });
  const resData = await resp.json();
  if (resp.ok) return { ok: true, data: resData };
  return { ok: false, error: resData.error || "Error al crear autor" };
}

export async function updateAuthor(id: string, data: Partial<Author>): Promise<{ ok: boolean; data?: Author; error?: string }> {
  const resp = await apiFetch(`/authors/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  });
  const resData = await resp.json();
  if (resp.ok) return { ok: true, data: resData };
  return { ok: false, error: resData.error || "Error al actualizar autor" };
}

// ─── Publication Types ───────────────────────────────────────────────────────

export async function getPublicationTypes(): Promise<PublicationType[]> {
  const resp = await apiFetch("/publication-types");
  if (resp.ok) return resp.json();
  return [];
}

export async function createPublicationType(data: { type_name: string }): Promise<{ ok: boolean; data?: PublicationType; error?: string }> {
  const resp = await apiFetch("/publication-types", {
    method: "POST",
    body: JSON.stringify(data)
  });
  const resData = await resp.json();
  if (resp.ok) return { ok: true, data: resData };
  return { ok: false, error: resData.error || "Error al crear tipo de publicación" };
}

// ─── Organizations ───────────────────────────────────────────────────────────

export interface Organization {
  organization_id: string;
  name: string;
  website?: string;
  country?: string;
  description?: string;
  created_at: string | null;
}

export async function getOrganizations(): Promise<Organization[]> {
  const resp = await apiFetch("/organizations");
  if (resp.ok) return resp.json();
  return [];
}

export async function createOrganization(data: { name: string; website?: string; country?: string; description?: string }): Promise<{ ok: boolean; data?: Organization; error?: string }> {
  const resp = await apiFetch("/organizations", {
    method: "POST",
    body: JSON.stringify(data)
  });
  const resData = await resp.json();
  if (resp.ok) return { ok: true, data: resData };
  return { ok: false, error: resData.error || "Error al crear organización" };
}

export async function updateOrganization(id: string, data: { name?: string; website?: string; country?: string; description?: string }): Promise<{ ok: boolean; data?: Organization; error?: string }> {
  const resp = await apiFetch(`/organizations/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  });
  const resData = await resp.json();
  if (resp.ok) return { ok: true, data: resData };
  return { ok: false, error: resData.error || "Error al actualizar organización" };
}

export async function deleteOrganization(id: string): Promise<boolean> {
  const resp = await apiFetch(`/organizations/${id}`, { method: "DELETE" });
  return resp.ok;
}

export async function deleteAuthor(id: string): Promise<boolean> {
  const resp = await apiFetch(`/authors/${id}`, { method: "DELETE" });
  return resp.ok;
}
