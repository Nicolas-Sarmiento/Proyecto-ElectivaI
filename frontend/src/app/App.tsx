import { useState } from 'react';
import { Search, Plus, Database, Brain } from 'lucide-react';
import { ArticleForm } from './components/ArticleForm';
import { ArticleList } from './components/ArticleList';
import { SearchPanel } from './components/SearchPanel';

export interface Article {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  journal: string;
  publicationDate: string;
  doi: string;
  keywords: string[];
  category: string;
}

// Mock data
const initialArticles: Article[] = [
  {
    id: '1',
    title: 'CRISPR-Cas9 Gene Editing: Applications and Future Prospects',
    authors: ['Dr. Sarah Chen', 'Dr. Michael Rodriguez'],
    abstract: 'This study explores the revolutionary CRISPR-Cas9 technology and its applications in treating genetic disorders. We demonstrate successful gene editing in human embryonic cells with 95% accuracy.',
    journal: 'Nature Biotechnology',
    publicationDate: '2025-12-15',
    doi: '10.1038/nbt.2025.001',
    keywords: ['CRISPR', 'gene editing', 'biotechnology', 'genetic disorders'],
    category: 'Biotechnology'
  },
  {
    id: '2',
    title: 'Quantum Computing Breakthrough in Prime Factorization',
    authors: ['Dr. James Wilson', 'Dr. Priya Sharma', 'Dr. Ahmed Hassan'],
    abstract: 'We present a novel quantum algorithm that factors large prime numbers exponentially faster than classical methods, with implications for cryptography and computational mathematics.',
    journal: 'Science',
    publicationDate: '2026-01-20',
    doi: '10.1126/science.2026.002',
    keywords: ['quantum computing', 'cryptography', 'algorithms', 'prime numbers'],
    category: 'Computer Science'
  },
  {
    id: '3',
    title: 'Climate Change Impact on Arctic Ecosystems: A Decade Study',
    authors: ['Dr. Emma Thompson', 'Dr. Lars Eriksson'],
    abstract: 'Ten years of field research reveal dramatic changes in Arctic biodiversity due to rising temperatures. We document a 40% decline in ice-dependent species populations.',
    journal: 'Environmental Science & Technology',
    publicationDate: '2026-03-10',
    doi: '10.1021/est.2026.003',
    keywords: ['climate change', 'Arctic', 'biodiversity', 'ecology'],
    category: 'Environmental Science'
  }
];

export default function App() {
  const [articles, setArticles] = useState<Article[]>(initialArticles);
  const [filteredArticles, setFilteredArticles] = useState<Article[]>(initialArticles);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [searchMode, setSearchMode] = useState<'natural' | 'structured'>('natural');

  const handleAddArticle = (article: Omit<Article, 'id'>) => {
    const newArticle: Article = {
      ...article,
      id: Date.now().toString()
    };
    const updatedArticles = [...articles, newArticle];
    setArticles(updatedArticles);
    setFilteredArticles(updatedArticles);
    setIsFormOpen(false);
  };

  const handleUpdateArticle = (updatedArticle: Article) => {
    const updatedArticles = articles.map(a => a.id === updatedArticle.id ? updatedArticle : a);
    setArticles(updatedArticles);
    setFilteredArticles(updatedArticles);
    setEditingArticle(null);
    setIsFormOpen(false);
  };

  const handleDeleteArticle = (id: string) => {
    const updatedArticles = articles.filter(a => a.id !== id);
    setArticles(updatedArticles);
    setFilteredArticles(updatedArticles);
  };

  const handleEdit = (article: Article) => {
    setEditingArticle(article);
    setIsFormOpen(true);
  };

  const handleSearch = (results: Article[]) => {
    setFilteredArticles(results);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingArticle(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Science Articles Database</h1>
          <p className="text-slate-600">Manage and search through scientific publications</p>
        </div>

        {/* Search Mode Toggle */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-sm font-medium text-slate-700">Search Mode:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setSearchMode('natural')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  searchMode === 'natural'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Brain className="w-4 h-4" />
                Natural Language
              </button>
              <button
                onClick={() => setSearchMode('structured')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  searchMode === 'structured'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Database className="w-4 h-4" />
                Structured Query
              </button>
            </div>
          </div>

          <SearchPanel
            articles={articles}
            onSearch={handleSearch}
            searchMode={searchMode}
          />
        </div>

        {/* Add Article Button */}
        <div className="mb-6">
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            <Plus className="w-5 h-5" />
            Add New Article
          </button>
        </div>

        {/* Article Form Modal */}
        {isFormOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <ArticleForm
                article={editingArticle}
                onSubmit={editingArticle ? handleUpdateArticle : handleAddArticle}
                onCancel={handleCloseForm}
              />
            </div>
          </div>
        )}

        {/* Articles List */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">
              Articles ({filteredArticles.length})
            </h2>
          </div>
          <ArticleList
            articles={filteredArticles}
            onEdit={handleEdit}
            onDelete={handleDeleteArticle}
          />
        </div>
      </div>
    </div>
  );
}
