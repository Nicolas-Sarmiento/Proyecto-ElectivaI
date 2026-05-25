import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Article } from '../App';

interface ArticleFormProps {
  article?: Article | null;
  onSubmit: (article: Article | Omit<Article, 'id'>) => void;
  onCancel: () => void;
}

export function ArticleForm({ article, onSubmit, onCancel }: ArticleFormProps) {
  const [formData, setFormData] = useState({
    title: '',
    authors: '',
    abstract: '',
    journal: '',
    publicationDate: '',
    doi: '',
    keywords: '',
    category: ''
  });

  useEffect(() => {
    if (article) {
      setFormData({
        title: article.title,
        authors: article.authors.join(', '),
        abstract: article.abstract,
        journal: article.journal,
        publicationDate: article.publicationDate,
        doi: article.doi,
        keywords: article.keywords.join(', '),
        category: article.category
      });
    }
  }, [article]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const articleData = {
      title: formData.title,
      authors: formData.authors.split(',').map(a => a.trim()),
      abstract: formData.abstract,
      journal: formData.journal,
      publicationDate: formData.publicationDate,
      doi: formData.doi,
      keywords: formData.keywords.split(',').map(k => k.trim()),
      category: formData.category
    };

    if (article) {
      onSubmit({ ...articleData, id: article.id });
    } else {
      onSubmit(articleData);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          {article ? 'Edit Article' : 'Add New Article'}
        </h2>
        <button
          onClick={onCancel}
          className="text-slate-400 hover:text-slate-600 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Authors (comma-separated) *
          </label>
          <input
            type="text"
            name="authors"
            value={formData.authors}
            onChange={handleChange}
            required
            placeholder="Dr. John Doe, Dr. Jane Smith"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Abstract *
          </label>
          <textarea
            name="abstract"
            value={formData.abstract}
            onChange={handleChange}
            required
            rows={4}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Journal *
            </label>
            <input
              type="text"
              name="journal"
              value={formData.journal}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Publication Date *
            </label>
            <input
              type="date"
              name="publicationDate"
              value={formData.publicationDate}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            DOI *
          </label>
          <input
            type="text"
            name="doi"
            value={formData.doi}
            onChange={handleChange}
            required
            placeholder="10.1234/example.2024.001"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Keywords (comma-separated) *
          </label>
          <input
            type="text"
            name="keywords"
            value={formData.keywords}
            onChange={handleChange}
            required
            placeholder="machine learning, AI, neural networks"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Category *
          </label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a category</option>
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

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {article ? 'Update Article' : 'Add Article'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 bg-slate-200 text-slate-700 px-6 py-3 rounded-lg hover:bg-slate-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
