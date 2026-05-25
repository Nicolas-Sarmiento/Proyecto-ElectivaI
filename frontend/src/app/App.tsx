import { useState, useEffect, useCallback } from 'react';
import { Plus, LogOut, User, BookOpen } from 'lucide-react';
import { LoginForm } from './components/LoginForm';
import { PublicationForm } from './components/ArticleForm';
import { PublicationList } from './components/ArticleList';
import { SearchPanel } from './components/SearchPanel';
import {
  isAuthenticated,
  logout,
  getMe,
  getPublications,
  deletePublication,
  type Publication,
} from './services/api';

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isAuthenticated());
  const [userName, setUserName] = useState('');
  const [publications, setPublications] = useState<Publication[]>([]);
  const [searchResults, setSearchResults] = useState<Publication[] | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPub, setEditingPub] = useState<Publication | null>(null);
  const [searchMode, setSearchMode] = useState<'natural' | 'keyword'>('keyword');
  const [loading, setLoading] = useState(false);

  // Cargar publicaciones al inicio
  const loadPublications = useCallback(async () => {
    setLoading(true);
    const pubs = await getPublications();
    setPublications(pubs);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (loggedIn) {
      loadPublications();
      getMe().then((user) => {
        if (user) setUserName(user.username || user.email || '');
      });
    }
  }, [loggedIn, loadPublications]);

  const handleLogout = async () => {
    await logout();
    setLoggedIn(false);
    setPublications([]);
    setSearchResults(null);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Estás seguro de eliminar esta publicación?')) return;
    const ok = await deletePublication(id);
    if (ok) {
      setPublications((prev) => prev.filter((p) => p.publication_id !== id));
      if (searchResults) {
        setSearchResults((prev) => prev!.filter((p) => p.publication_id !== id));
      }
    }
  };

  const handleEdit = (pub: Publication) => {
    setEditingPub(pub);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingPub(null);
  };

  const handleFormSuccess = () => {
    handleFormClose();
    loadPublications();
    setSearchResults(null);
  };

  const handleSearchResults = (results: Publication[]) => {
    setSearchResults(results);
  };

  const handleClearSearch = () => {
    setSearchResults(null);
  };

  // Si no está autenticado, mostrar login
  if (!loggedIn) {
    return <LoginForm onLoginSuccess={() => setLoggedIn(true)} />;
  }

  const displayedPubs = searchResults !== null ? searchResults : publications;
  const isSemanticResults = searchResults !== null && searchMode === 'natural';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* ─── Navbar ─────────────────────────────────────────────── */}
      <nav className="bg-white/80 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 shadow-md shadow-blue-500/20">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-slate-900">
              Sistema Editorial
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <User className="w-4 h-4" />
              <span>{userName}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Cerrar sesión
            </button>
          </div>
        </div>
      </nav>

      {/* ─── Main content ───────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Search section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <SearchPanel
            searchMode={searchMode}
            onSearchModeChange={setSearchMode}
            onSearch={handleSearchResults}
            onClear={handleClearSearch}
          />
        </div>

        {/* Actions bar */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              {isSemanticResults
                ? `Resultados Semánticos (${displayedPubs.length})`
                : searchResults !== null
                  ? `Resultados por Palabra Clave (${displayedPubs.length})`
                  : `Publicaciones (${displayedPubs.length})`}
            </h2>
            {isSemanticResults && (
              <p className="text-sm text-slate-500 mt-1">
                Ordenados por relevancia semántica
              </p>
            )}
          </div>
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:from-blue-500 hover:to-indigo-500 transition-all shadow-md shadow-blue-500/20 hover:shadow-blue-500/30"
          >
            <Plus className="w-5 h-5" />
            Nueva Publicación
          </button>
        </div>

        {/* Publication list */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500 mt-4">Cargando publicaciones...</p>
          </div>
        ) : (
          <PublicationList
            publications={displayedPubs}
            isSemanticSearch={isSemanticResults}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
      </div>

      {/* ─── Publication Form Modal ────────────────────────────── */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <PublicationForm
              publication={editingPub}
              onSuccess={handleFormSuccess}
              onCancel={handleFormClose}
            />
          </div>
        </div>
      )}
    </div>
  );
}
