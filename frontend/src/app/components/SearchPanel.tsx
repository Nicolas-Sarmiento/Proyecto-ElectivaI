import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { Article } from '../App';

interface SearchPanelProps {
  articles: Article[];
  onSearch: (results: Article[]) => void;
  searchMode: 'natural' | 'structured';
}

export function SearchPanel({ articles, onSearch, searchMode }: SearchPanelProps) {
  const [naturalQuery, setNaturalQuery] = useState('');
  const [structuredQuery, setStructuredQuery] = useState({
    title: '',
    author: '',
    journal: '',
    category: '',
    keyword: '',
    dateFrom: '',
    dateTo: ''
  });

  useEffect(() => {
    if (searchMode === 'natural') {
      handleNaturalSearch();
    } else {
      handleStructuredSearch();
    }
  }, [naturalQuery, structuredQuery, searchMode, articles]);

  const handleNaturalSearch = () => {
    if (!naturalQuery.trim()) {
      onSearch(articles);
      return;
    }

    const query = naturalQuery.toLowerCase();
    const results = articles.filter(article => {
      const searchableText = [
        article.title,
        article.abstract,
        article.journal,
        article.category,
        ...article.authors,
        ...article.keywords,
        article.doi
      ].join(' ').toLowerCase();

      return searchableText.includes(query);
    });

    onSearch(results);
  };

  const handleStructuredSearch = () => {
    let results = articles;

    if (structuredQuery.title) {
      results = results.filter(article =>
        article.title.toLowerCase().includes(structuredQuery.title.toLowerCase())
      );
    }

    if (structuredQuery.author) {
      results = results.filter(article =>
        article.authors.some(author =>
          author.toLowerCase().includes(structuredQuery.author.toLowerCase())
        )
      );
    }

    if (structuredQuery.journal) {
      results = results.filter(article =>
        article.journal.toLowerCase().includes(structuredQuery.journal.toLowerCase())
      );
    }

    if (structuredQuery.category) {
      results = results.filter(article =>
        article.category === structuredQuery.category
      );
    }

    if (structuredQuery.keyword) {
      results = results.filter(article =>
        article.keywords.some(keyword =>
          keyword.toLowerCase().includes(structuredQuery.keyword.toLowerCase())
        )
      );
    }

    if (structuredQuery.dateFrom) {
      results = results.filter(article =>
        article.publicationDate >= structuredQuery.dateFrom
      );
    }

    if (structuredQuery.dateTo) {
      results = results.filter(article =>
        article.publicationDate <= structuredQuery.dateTo
      );
    }

    onSearch(results);
  };

  const handleStructuredChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setStructuredQuery({
      ...structuredQuery,
      [e.target.name]: e.target.value
    });
  };

  const clearNaturalSearch = () => {
    setNaturalQuery('');
  };

  const clearStructuredSearch = () => {
    setStructuredQuery({
      title: '',
      author: '',
      journal: '',
      category: '',
      keyword: '',
      dateFrom: '',
      dateTo: ''
    });
  };

  if (searchMode === 'natural') {
    return (
      <div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input
            type="text"
            value={naturalQuery}
            onChange={(e) => setNaturalQuery(e.target.value)}
            placeholder="Search articles using natural language... (e.g., 'gene editing', 'quantum computing breakthrough')"
            className="w-full pl-10 pr-10 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {naturalQuery && (
            <button
              onClick={clearNaturalSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        <p className="text-sm text-slate-500 mt-2">
          Search across titles, abstracts, authors, keywords, journals, and more
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Title
          </label>
          <input
            type="text"
            name="title"
            value={structuredQuery.title}
            onChange={handleStructuredChange}
            placeholder="Filter by title"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Author
          </label>
          <input
            type="text"
            name="author"
            value={structuredQuery.author}
            onChange={handleStructuredChange}
            placeholder="Filter by author"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Journal
          </label>
          <input
            type="text"
            name="journal"
            value={structuredQuery.journal}
            onChange={handleStructuredChange}
            placeholder="Filter by journal"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Category
          </label>
          <select
            name="category"
            value={structuredQuery.category}
            onChange={handleStructuredChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            <option value="Biotechnology">Biotechnology</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Environmental Science">Environmental Science</option>
            <option value="Physics">Physics</option>
            <option value="Chemistry">Chemistry</option>
            <option value="Medicine">Medicine</option>
            <option value="Neuroscience">Neuroscience</option>
            <option value="Mathematics">Mathematics</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Keyword
          </label>
          <input
            type="text"
            name="keyword"
            value={structuredQuery.keyword}
            onChange={handleStructuredChange}
            placeholder="Filter by keyword"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Date From
          </label>
          <input
            type="date"
            name="dateFrom"
            value={structuredQuery.dateFrom}
            onChange={handleStructuredChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Date To
          </label>
          <input
            type="date"
            name="dateTo"
            value={structuredQuery.dateTo}
            onChange={handleStructuredChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={clearStructuredSearch}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          <X className="w-4 h-4" />
          Clear All Filters
        </button>
      </div>

      <p className="text-sm text-slate-500">
        Use specific fields to build precise queries. Combine multiple filters for advanced searches.
      </p>
    </div>
  );
}
