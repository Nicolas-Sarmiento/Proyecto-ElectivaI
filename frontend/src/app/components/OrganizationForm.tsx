import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { createOrganization, updateOrganization, type Organization } from '../services/api';

interface OrganizationFormProps {
  organization?: Organization | null;
  onSuccess: (org: Organization) => void;
  onCancel: () => void;
}

export function OrganizationForm({ organization, onSuccess, onCancel }: OrganizationFormProps) {
  const [name, setName] = useState(organization?.name || '');
  const [website, setWebsite] = useState(organization?.website || '');
  const [country, setCountry] = useState(organization?.country || '');
  const [description, setDescription] = useState(organization?.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload = { name, website, country, description };

    let res;
    if (organization) {
      res = await updateOrganization(organization.organization_id, payload);
    } else {
      res = await createOrganization(payload);
    }

    if (res.ok && res.data) {
      onSuccess(res.data);
    } else {
      setError(res.error || 'Error al guardar organización');
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          {organization ? 'Editar Organización' : 'Nueva Organización'}
        </h2>
        <button onClick={onCancel} className="text-slate-400 hover:text-slate-600">
          <X className="w-6 h-6" />
        </button>
      </div>

      {error && <div className="text-red-600 bg-red-50 p-3 rounded-lg mb-4">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre *</label>
          <input type="text" required value={name} onChange={e => setName(e.target.value)} className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Sitio Web</label>
            <input type="url" value={website} onChange={e => setWebsite(e.target.value)} placeholder="https://..." className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">País</label>
            <input type="text" value={country} onChange={e => setCountry(e.target.value)} className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Descripción</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500 h-24" placeholder="Información relevante sobre la editorial..." />
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
