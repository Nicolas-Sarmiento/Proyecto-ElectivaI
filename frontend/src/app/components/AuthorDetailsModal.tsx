import { useState, useEffect } from 'react';
import { X, Building2, MapPin, Globe, Loader2 } from 'lucide-react';
import { type Author, type Publication, getPublicationsByAuthor } from '../services/api';
import { PublicationList } from './ArticleList';

interface AuthorDetailsModalProps {
  author: Author;
  onClose: () => void;
  onEditPublication?: (pub: Publication) => void;
  onDeletePublication?: (id: string) => void;
  isAdmin?: boolean;
}

export function AuthorDetailsModal({ author, onClose, onEditPublication, onDeletePublication, isAdmin }: AuthorDetailsModalProps) {
  const [publications, setPublications] = useState<Publication[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPublicationsByAuthor(author.author_id)
      .then(setPublications)
      .finally(() => setLoading(false));
  }, [author]);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-start justify-between mb-6 border-b pb-4">
          <div>
            <h2 className="text-3xl font-bold text-slate-900 mb-2">
              {author.first_name} {author.last_name}
            </h2>
            <div className="flex flex-wrap gap-4 text-sm text-slate-600">
              {author.organization && (
                <div className="flex items-center gap-1.5">
                  <Building2 className="w-4 h-4" />
                  {author.organization.name}
                </div>
              )}
              {author.country && (
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  {author.country}
                </div>
              )}
              {author.orcid_url && (
                <a href={author.orcid_url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-blue-600 hover:underline">
                  <Globe className="w-4 h-4" />
                  ORCID
                </a>
              )}
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-4">Trabajos relacionados ({publications.length})</h3>
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-blue-600" /></div>
          ) : (
            <PublicationList
              publications={publications}
              isSemanticSearch={false}
              onEdit={onEditPublication || (() => {})}
              onDelete={onDeletePublication || (() => {})}
              isAdmin={isAdmin}
            />
          )}
        </div>
      </div>
    </div>
  );
}
