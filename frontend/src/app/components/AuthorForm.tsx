import { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import { createAuthor, updateAuthor, getOrganizations, type Author, type Organization } from '../services/api';

interface AuthorFormProps {
  author?: Author | null;
  onSuccess: (author: Author) => void;
  onCancel: () => void;
}

export function AuthorForm({ author, onSuccess, onCancel }: AuthorFormProps) {
  const [firstName, setFirstName] = useState(author?.first_name || '');
  const [lastName, setLastName] = useState(author?.last_name || '');
  const [country, setCountry] = useState(author?.country || '');
  const [orcidUrl, setOrcidUrl] = useState(author?.orcid_url || '');
  const [organizationId, setOrganizationId] = useState(author?.organization?.organization_id || '');
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getOrganizations().then(setOrganizations);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const data = {
      first_name: firstName,
      last_name: lastName,
      country: country || undefined,
      orcid_url: orcidUrl || undefined,
      organization_id: organizationId || undefined,
    };

    let res;
    if (author) {
      res = await updateAuthor(author.author_id, data);
    } else {
      res = await createAuthor(data);
    }

    if (res.ok && res.data) {
      onSuccess(res.data);
    } else {
      setError(res.error || 'Error al guardar autor');
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          {author ? 'Editar Autor' : 'Nuevo Autor'}
        </h2>
        <button onClick={onCancel} className="text-slate-400 hover:text-slate-600">
          <X className="w-6 h-6" />
        </button>
      </div>

      {error && <div className="text-red-600 bg-red-50 p-3 rounded-lg mb-4">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nombres *</label>
            <input type="text" required value={firstName} onChange={e => setFirstName(e.target.value)} className="w-full border rounded-lg p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Apellidos *</label>
            <input type="text" required value={lastName} onChange={e => setLastName(e.target.value)} className="w-full border rounded-lg p-2" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">País</label>
          <input type="text" value={country} onChange={e => setCountry(e.target.value)} className="w-full border rounded-lg p-2" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">URL de ORCID</label>
          <input type="url" value={orcidUrl} onChange={e => setOrcidUrl(e.target.value)} placeholder="https://orcid.org/0000-0000-0000-0000" className="w-full border rounded-lg p-2" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Organización</label>
          <select value={organizationId} onChange={e => setOrganizationId(e.target.value)} className="w-full border rounded-lg p-2">
            <option value="">Sin organización</option>
            {organizations.map(o => (
              <option key={o.organization_id} value={o.organization_id}>{o.name}</option>
            ))}
          </select>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button type="button" onClick={onCancel} className="px-4 py-2 text-slate-600 bg-slate-100 rounded-lg">Cancelar</button>
          <button type="submit" disabled={loading} className="px-4 py-2 text-white bg-blue-600 rounded-lg flex items-center gap-2">
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            Guardar
          </button>
        </div>
      </form>
    </div>
  );
}
