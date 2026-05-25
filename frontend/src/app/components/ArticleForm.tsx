import { useState, useEffect } from 'react';
import { X, Upload, Loader2, Plus } from 'lucide-react';
import {
  createPublication,
  updatePublication,
  getAuthors,
  getPublicationTypes,
  createAuthor,
  createPublicationType,
  type Publication,
  type Author,
  type PublicationType,
} from '../services/api';

interface PublicationFormProps {
  publication?: Publication | null;
  onSuccess: () => void;
  onCancel: () => void;
  isAdmin?: boolean;
}

export function PublicationForm({ publication, onSuccess, onCancel, isAdmin }: PublicationFormProps) {
  const [title, setTitle] = useState('');
  const [typeId, setTypeId] = useState('');
  const [publishDate, setPublishDate] = useState('');
  const [keywordsList, setKeywordsList] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [selectedAuthors, setSelectedAuthors] = useState<string[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [authors, setAuthors] = useState<Author[]>([]);
  const [pubTypes, setPubTypes] = useState<PublicationType[]>([]);

  useEffect(() => {
    getAuthors().then(setAuthors);
    getPublicationTypes().then(setPubTypes);
  }, []);

  useEffect(() => {
    if (publication) {
      setTitle(publication.title);
      setTypeId(publication.publication_type?.type_id || '');
      setPublishDate(
        publication.publish_date
          ? publication.publish_date.split('T')[0]
          : ''
      );
      setKeywordsList(publication.keywords || []);
      setSelectedAuthors(publication.authors.map((a) => a.author_id));
    }
  }, [publication]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('title', title);
    if (typeId) formData.append('type_id', typeId);
    if (publishDate) formData.append('publish_date', publishDate);

    const finalKeywords = [...keywordsList];
    if (keywordInput.trim() && !finalKeywords.includes(keywordInput.trim())) {
      finalKeywords.push(keywordInput.trim());
    }
    finalKeywords.forEach((kw) => formData.append('keywords', kw));

    selectedAuthors.forEach((id) => formData.append('author_ids', id));

    if (file) formData.append('file', file);

    let result;
    if (publication) {
      result = await updatePublication(publication.publication_id, formData);
    } else {
      if (!file) {
        setError('Se requiere un archivo PDF.');
        setLoading(false);
        return;
      }
      result = await createPublication(formData);
    }

    if (result.ok) {
      onSuccess();
    } else {
      setError(result.error || 'Error desconocido');
    }
    setLoading(false);
  };

  const toggleAuthor = (id: string) => {
    setSelectedAuthors((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const handleKeywordKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = keywordInput.trim();
      if (val && !keywordsList.includes(val)) {
        setKeywordsList([...keywordsList, val]);
      }
      setKeywordInput('');
    }
  };

  const removeKeyword = (kwToRemove: string) => {
    setKeywordsList(keywordsList.filter(k => k !== kwToRemove));
  };

  const handleCreateAuthor = async () => {
    const firstName = window.prompt("Nombre del autor:");
    if (!firstName) return;
    const lastName = window.prompt("Apellido del autor:");
    if (!lastName) return;

    setLoading(true);
    const result = await createAuthor({ first_name: firstName, last_name: lastName });
    if (result.ok && result.data) {
      getAuthors().then(setAuthors);
      setSelectedAuthors(prev => [...prev, result.data!.author_id]);
    } else {
      alert(result.error);
    }
    setLoading(false);
  };

  const handleCreateType = async () => {
    const typeName = window.prompt("Nombre del nuevo tipo de publicación:");
    if (!typeName) return;

    setLoading(true);
    const result = await createPublicationType({ type_name: typeName });
    if (result.ok && result.data) {
      getPublicationTypes().then(setPubTypes);
      setTypeId(result.data.type_id);
    } else {
      alert(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          {publication ? 'Editar Publicación' : 'Nueva Publicación'}
        </h2>
        <button
          onClick={onCancel}
          className="text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 mb-4 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Título */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Título *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Tipo de publicación */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium text-slate-700">
                Tipo de Publicación
              </label>
              {isAdmin && (
                <button
                  type="button"
                  onClick={handleCreateType}
                  className="text-xs flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium bg-blue-50 px-2 py-0.5 rounded-md"
                >
                  <Plus className="w-3 h-3" /> Nuevo
                </button>
              )}
            </div>
            <select
              value={typeId}
              onChange={(e) => setTypeId(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
              <option value="">Sin tipo</option>
              {pubTypes.map((t) => (
                <option key={t.type_id} value={t.type_id}>
                  {t.type_name}
                </option>
              ))}
            </select>
          </div>

          {/* Fecha */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Fecha de Publicación
            </label>
            <input
              type="date"
              value={publishDate}
              onChange={(e) => setPublishDate(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            />
          </div>
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Palabras Clave (Presiona Enter para agregar)
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {keywordsList.map(kw => (
              <span key={kw} className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 border border-indigo-200 px-3 py-1 rounded-full text-sm">
                {kw}
                <button type="button" onClick={() => removeKeyword(kw)} className="hover:text-indigo-900">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            onKeyDown={handleKeywordKeyDown}
            placeholder="Añadir palabra clave..."
            className="w-full px-4 py-2.5 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
        </div>

        {/* Autores */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-slate-700">
              Autores
            </label>
            {isAdmin && (
              <button
                type="button"
                onClick={handleCreateAuthor}
                className="text-xs flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium bg-blue-50 px-2 py-0.5 rounded-md"
              >
                <Plus className="w-3 h-3" /> Nuevo Autor
              </button>
            )}
          </div>
          {authors.length === 0 ? (
            <p className="text-sm text-slate-400 italic">
              No hay autores registrados.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border border-slate-200 rounded-xl bg-slate-50">
              {authors.map((a) => (
                <button
                  key={a.author_id}
                  type="button"
                  onClick={() => toggleAuthor(a.author_id)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    selectedAuthors.includes(a.author_id)
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300'
                  }`}
                >
                  {a.first_name} {a.last_name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Archivo PDF */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Archivo PDF {!publication && '*'}
          </label>
          <label className="flex items-center justify-center gap-3 w-full px-4 py-6 border-2 border-dashed border-slate-300 rounded-xl cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 transition-all">
            <Upload className="w-5 h-5 text-slate-400" />
            <span className="text-sm text-slate-500">
              {file
                ? file.name
                : publication?.resource_url
                  ? `Archivo actual: ${publication.resource_url.split('_').slice(1).join('_')}`
                  : 'Seleccionar archivo PDF'}
            </span>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
            />
          </label>
        </div>

        {/* Botones */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 transition-all shadow-md"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {publication ? 'Actualizando...' : 'Creando y generando embeddings...'}
              </>
            ) : (
              publication ? 'Actualizar Publicación' : 'Crear Publicación'
            )}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 bg-slate-100 text-slate-700 px-6 py-3 rounded-xl hover:bg-slate-200 transition-colors"
          >
            Cancelar
          </button>
        </div>

        {!publication && (
          <p className="text-xs text-slate-400 text-center">
            Al crear la publicación, el contenido del PDF se procesará automáticamente para habilitar la búsqueda semántica.
          </p>
        )}
      </form>
    </div>
  );
}
