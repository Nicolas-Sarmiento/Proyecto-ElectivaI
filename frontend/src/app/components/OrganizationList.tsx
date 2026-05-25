import { useState, useEffect } from 'react';
import { Building2, Trash2, Plus, Edit2, Globe, MapPin } from 'lucide-react';
import { getOrganizations, deleteOrganization, type Organization } from '../services/api';
import { OrganizationForm } from './OrganizationForm';
import { OrganizationDetailsModal } from './OrganizationDetailsModal';

export function OrganizationList({ isAdmin }: { isAdmin: boolean }) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    setLoading(true);
    const data = await getOrganizations();
    setOrganizations(data);
    setLoading(false);
  };

  const handleCreate = () => {
    setEditingOrg(null);
    setIsFormOpen(true);
  };

  const handleEdit = (org: Organization) => {
    setEditingOrg(org);
    setIsFormOpen(true);
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    loadOrganizations();
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("¿Seguro que deseas eliminar esta organización?")) return;
    const ok = await deleteOrganization(id);
    if (ok) {
      setOrganizations(prev => prev.filter(o => o.organization_id !== id));
    } else {
      alert("Error al eliminar organización");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Editoriales y Organizaciones ({organizations.length})</h2>
        {isAdmin && (
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-md"
          >
            <Plus className="w-5 h-5" />
            Nueva Editorial
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-500">Cargando organizaciones...</div>
      ) : organizations.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
          <p className="text-slate-500">No hay organizaciones registradas</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {organizations.map(org => (
            <div key={org.organization_id} className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition-all group flex flex-col justify-between items-start cursor-pointer" onClick={() => setSelectedOrg(org)}>
              <div className="w-full">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-blue-500" />
                    <h3 className="font-semibold text-slate-800 text-lg group-hover:text-blue-600 transition-colors">{org.name}</h3>
                  </div>
                  {isAdmin && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                  <button
                    onClick={() => handleEdit(org)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Editar"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(org.organization_id)}
                    className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
            
            <div className="space-y-1.5 mt-3 ml-7 w-full">
              {org.country && (
                <p className="text-sm text-slate-600 flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  {org.country}
                </p>
              )}
              {org.website && (
                <a href={org.website} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()} className="text-sm text-blue-600 hover:underline flex items-center gap-1.5">
                  <Globe className="w-4 h-4 text-slate-400" />
                  Sitio Web
                </a>
              )}
              {org.description && (
                <p className="text-sm text-slate-500 line-clamp-2 mt-2">
                  {org.description}
                </p>
              )}
            </div>
            </div>
          </div>
          ))}
        </div>
      )}

      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <OrganizationForm
              organization={editingOrg}
              onSuccess={handleFormSuccess}
              onCancel={() => setIsFormOpen(false)}
            />
          </div>
        </div>
      )}

      {selectedOrg && (
        <OrganizationDetailsModal
          organization={selectedOrg}
          onClose={() => setSelectedOrg(null)}
        />
      )}
    </div>
  );
}
