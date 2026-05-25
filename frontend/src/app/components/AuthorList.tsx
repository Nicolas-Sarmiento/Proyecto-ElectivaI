import { useState, useEffect } from 'react';
import { User, Trash2, Plus, Edit2, MapPin, Building2, Globe } from 'lucide-react';
import { getAuthors, deleteAuthor, type Author } from '../services/api';
import { AuthorForm } from './AuthorForm';
import { AuthorDetailsModal } from './AuthorDetailsModal';

export function AuthorList({ isAdmin }: { isAdmin: boolean }) {
  const [authors, setAuthors] = useState<Author[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAuthor, setEditingAuthor] = useState<Author | null>(null);
  const [selectedAuthor, setSelectedAuthor] = useState<Author | null>(null);

  useEffect(() => {
    loadAuthors();
  }, []);

  const loadAuthors = async () => {
    setLoading(true);
    const data = await getAuthors();
    setAuthors(data);
    setLoading(false);
  };

  const handleCreate = () => {
    setEditingAuthor(null);
    setIsFormOpen(true);
  };

  const handleEdit = (author: Author) => {
    setEditingAuthor(author);
    setIsFormOpen(true);
  };

  const handleFormSuccess = (author: Author) => {
    setIsFormOpen(false);
    loadAuthors();
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("¿Seguro que deseas eliminar este autor?")) return;
    const ok = await deleteAuthor(id);
    if (ok) {
      setAuthors(prev => prev.filter(a => a.author_id !== id));
    } else {
      alert("Error al eliminar autor");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Autores ({authors.length})</h2>
        {isAdmin && (
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-md"
          >
            <Plus className="w-5 h-5" />
            Nuevo Autor
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-500">Cargando autores...</div>
      ) : authors.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
          <p className="text-slate-500">No hay autores registrados</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {authors.map(author => (
            <div key={author.author_id} className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition-all group flex flex-col justify-between items-start cursor-pointer" onClick={() => setSelectedAuthor(author)}>
              <div className="w-full">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <User className="w-5 h-5 text-blue-500" />
                    <h3 className="font-semibold text-slate-800 text-lg group-hover:text-blue-600 transition-colors">{author.first_name} {author.last_name}</h3>
                  </div>
                  {isAdmin && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={() => handleEdit(author)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Editar"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(author.author_id)}
                        className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
                <div className="space-y-1.5 mt-3 ml-7">
                  {author.organization && (
                    <p className="text-sm text-slate-600 flex items-center gap-1.5">
                      <Building2 className="w-4 h-4 text-slate-400" />
                      {author.organization.name}
                    </p>
                  )}
                  {author.country && (
                    <p className="text-sm text-slate-600 flex items-center gap-1.5">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      {author.country}
                    </p>
                  )}
                  {author.orcid_url && (
                    <a href={author.orcid_url} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()} className="text-sm text-blue-600 hover:underline flex items-center gap-1.5">
                      <Globe className="w-4 h-4 text-slate-400" />
                      ORCID
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <AuthorForm
              author={editingAuthor}
              onSuccess={handleFormSuccess}
              onCancel={() => setIsFormOpen(false)}
            />
          </div>
        </div>
      )}

      {selectedAuthor && (
        <AuthorDetailsModal
          author={selectedAuthor}
          onClose={() => setSelectedAuthor(null)}
          isAdmin={isAdmin}
        />
      )}
    </div>
  );
}
