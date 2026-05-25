import { Edit2, Trash2, Calendar, Tag, Download, FileText, Brain } from 'lucide-react';
import { type Publication, getFileDownloadUrl } from '../services/api';

interface PublicationListProps {
  publications: Publication[];
  isSemanticSearch: boolean;
  onEdit: (pub: Publication) => void;
  onDelete: (id: string) => void;
}

export function PublicationList({
  publications,
  isSemanticSearch,
  onEdit,
  onDelete,
}: PublicationListProps) {
  if (publications.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <p className="text-slate-500 text-lg">No se encontraron publicaciones</p>
        <p className="text-slate-400 text-sm mt-2">
          Intenta con otros términos de búsqueda o crea una nueva publicación
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {publications.map((pub) => (
        <div
          key={pub.publication_id}
          className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg hover:border-slate-300 transition-all group"
        >
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-slate-900 mb-1 group-hover:text-blue-700 transition-colors">
                {pub.title}
              </h3>
              {pub.authors.length > 0 && (
                <p className="text-sm text-slate-500">
                  {pub.authors.map((a) => `${a.first_name} ${a.last_name}`).join(', ')}
                </p>
              )}
            </div>
            <div className="flex gap-1 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => onEdit(pub)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Editar"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete(pub.publication_id)}
                className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="Eliminar"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Similarity score for semantic results */}
          {isSemanticSearch && pub.similarity !== undefined && (
            <div className="mb-4 p-3 bg-purple-50 border border-purple-100 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-semibold text-purple-700">
                  Relevancia: {(pub.similarity * 100).toFixed(1)}%
                </span>
                {pub.matched_page && (
                  <span className="text-xs text-purple-500 ml-auto">
                    Página {pub.matched_page}
                  </span>
                )}
              </div>
              {/* Similarity bar */}
              <div className="w-full bg-purple-100 rounded-full h-1.5 mb-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-indigo-500 h-1.5 rounded-full transition-all"
                  style={{ width: `${Math.min(pub.similarity * 100, 100)}%` }}
                />
              </div>
              {pub.matched_text && (
                <p className="text-xs text-purple-600/80 line-clamp-2 italic">
                  "...{pub.matched_text.slice(0, 200)}..."
                </p>
              )}
            </div>
          )}

          {/* Metadata row */}
          <div className="flex flex-wrap items-center gap-4 mb-3 text-sm text-slate-500">
            {pub.publication_type && (
              <span className="px-2.5 py-0.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium">
                {pub.publication_type.type_name}
              </span>
            )}
            {pub.publish_date && (
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                <span>{new Date(pub.publish_date).toLocaleDateString('es-CO')}</span>
              </div>
            )}
            {pub.resource_url && (
              <a
                href={getFileDownloadUrl(pub.publication_id)}
                className="flex items-center gap-1.5 text-blue-600 hover:text-blue-700 hover:underline"
                target="_blank"
                rel="noreferrer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Descargar PDF</span>
              </a>
            )}
          </div>

          {/* Keywords */}
          {pub.keywords && pub.keywords.length > 0 && (
            <div className="flex items-start gap-2">
              <Tag className="w-3.5 h-3.5 text-slate-400 mt-1 flex-shrink-0" />
              <div className="flex flex-wrap gap-1.5">
                {pub.keywords.map((kw, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-lg"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
