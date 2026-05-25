import { X, Building2, MapPin, Globe, AlignLeft } from 'lucide-react';
import { type Organization } from '../services/api';

interface OrganizationDetailsModalProps {
  organization: Organization;
  onClose: () => void;
}

export function OrganizationDetailsModal({ organization, onClose }: OrganizationDetailsModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-start justify-between mb-6 border-b pb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900">
                {organization.name}
              </h2>
            </div>
            
            <div className="flex flex-wrap gap-4 text-sm text-slate-600 mt-3 ml-1">
              {organization.country && (
                <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1 rounded-full">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  {organization.country}
                </div>
              )}
              {organization.website && (
                <a 
                  href={organization.website} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center gap-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors px-3 py-1 rounded-full"
                >
                  <Globe className="w-4 h-4" />
                  Sitio Web
                </a>
              )}
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-3">
              <AlignLeft className="w-5 h-5 text-blue-500" />
              Información Relevante
            </h3>
            {organization.description ? (
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-slate-700 whitespace-pre-wrap leading-relaxed">
                {organization.description}
              </div>
            ) : (
              <p className="text-slate-400 italic">No hay descripción disponible para esta organización.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
