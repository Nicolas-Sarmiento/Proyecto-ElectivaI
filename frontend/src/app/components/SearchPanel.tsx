import { useState } from 'react';
import { Search, X, Brain, Tag, Loader2 } from 'lucide-react';
import { getPublications, semanticSearch, type Publication } from '../services/api';

interface SearchPanelProps {
  searchMode: 'natural' | 'keyword';
  onSearchModeChange: (mode: 'natural' | 'keyword') => void;
  onSearch: (results: Publication[]) => void;
  onClear: () => void;
}

export function SearchPanel({
  searchMode,
  onSearchModeChange,
  onSearch,
  onClear,
}: SearchPanelProps) {
  const [naturalQuery, setNaturalQuery] = useState('');
  const [keywordQuery, setKeywordQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleNaturalSearch = async () => {
    const q = naturalQuery.trim();
    if (!q) {
      onClear();
      return;
    }
    setLoading(true);
    try {
      const results = await semanticSearch(q);
      onSearch(results);
    } catch (e) {
      console.error('Error en búsqueda semántica:', e);
    }
    setLoading(false);
  };

  const handleKeywordSearch = async () => {
    const kw = keywordQuery.trim();
    if (!kw) {
      onClear();
      return;
    }
    setLoading(true);
    try {
      const results = await getPublications(kw);
      onSearch(results);
    } catch (e) {
      console.error('Error en búsqueda por keyword:', e);
    }
    setLoading(false);
  };

  const handleNaturalKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleNaturalSearch();
  };

  const handleKeywordKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleKeywordSearch();
  };

  const clearNatural = () => {
    setNaturalQuery('');
    onClear();
  };

  const clearKeyword = () => {
    setKeywordQuery('');
    onClear();
  };

  return (
    <div>
      {/* Mode toggle */}
      <div className="flex items-center gap-4 mb-4">
        <span className="text-sm font-medium text-slate-700">Modo de búsqueda:</span>
        <div className="flex gap-2">
          <button
            onClick={() => { onSearchModeChange('natural'); onClear(); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              searchMode === 'natural'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md shadow-purple-500/20'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Brain className="w-4 h-4" />
            Lenguaje Natural
          </button>
          <button
            onClick={() => { onSearchModeChange('keyword'); onClear(); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              searchMode === 'keyword'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Tag className="w-4 h-4" />
            Palabra Clave
          </button>
        </div>
      </div>

      {/* Search input */}
      {searchMode === 'natural' ? (
        <div>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={naturalQuery}
              onChange={(e) => setNaturalQuery(e.target.value)}
              onKeyDown={handleNaturalKeyDown}
              placeholder="Describe lo que buscas... Ej: 'investigaciones sobre cambio climático en ecosistemas marinos'"
              className="w-full pl-12 pr-24 py-3.5 border border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-400 bg-purple-50/30 text-slate-800 placeholder-slate-400 transition-all"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {naturalQuery && (
                <button
                  onClick={clearNatural}
                  className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={handleNaturalSearch}
                disabled={loading || !naturalQuery.trim()}
                className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm rounded-lg hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 transition-all"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Buscar'}
              </button>
            </div>
          </div>
          <p className="text-xs text-purple-400 mt-2 ml-1">
             Búsqueda semántica — Busca por significado en el contenido de los PDFs usando IA
          </p>
        </div>
      ) : (
        <div>
          <div className="relative">
            <Tag className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={keywordQuery}
              onChange={(e) => setKeywordQuery(e.target.value)}
              onKeyDown={handleKeywordKeyDown}
              placeholder="Buscar por palabra clave exacta... Ej: 'machine learning'"
              className="w-full pl-12 pr-24 py-3.5 border border-blue-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400 bg-blue-50/30 text-slate-800 placeholder-slate-400 transition-all"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {keywordQuery && (
                <button
                  onClick={clearKeyword}
                  className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={handleKeywordSearch}
                disabled={loading || !keywordQuery.trim()}
                className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-sm rounded-lg hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 transition-all"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Buscar'}
              </button>
            </div>
          </div>
          <p className="text-xs text-blue-400 mt-2 ml-1">
             Búsqueda por keyword — Filtra publicaciones que contengan esta palabra clave exacta
          </p>
        </div>
      )}
    </div>
  );
}
