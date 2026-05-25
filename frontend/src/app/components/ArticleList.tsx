import { Edit2, Trash2, Calendar, BookOpen, Tag } from 'lucide-react';
import { Article } from '../App';

interface ArticleListProps {
  articles: Article[];
  onEdit: (article: Article) => void;
  onDelete: (id: string) => void;
}

export function ArticleList({ articles, onEdit, onDelete }: ArticleListProps) {
  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 text-lg">No articles found</p>
        <p className="text-slate-400 text-sm mt-2">Try adjusting your search or add a new article</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {articles.map((article) => (
        <div
          key={article.id}
          className="border border-slate-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-white"
        >
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-slate-900 mb-2">{article.title}</h3>
              <p className="text-sm text-slate-600 mb-2">
                {article.authors.join(', ')}
              </p>
            </div>
            <div className="flex gap-2 ml-4">
              <button
                onClick={() => onEdit(article)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit article"
              >
                <Edit2 className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to delete this article?')) {
                    onDelete(article.id);
                  }
                }}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete article"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>

          <p className="text-slate-700 mb-4 leading-relaxed">{article.abstract}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <BookOpen className="w-4 h-4" />
              <span>{article.journal}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Calendar className="w-4 h-4" />
              <span>{new Date(article.publicationDate).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="mb-3">
            <span className="text-sm text-slate-600">DOI: </span>
            <span className="text-sm text-blue-600 font-mono">{article.doi}</span>
          </div>

          <div className="flex items-start gap-2">
            <Tag className="w-4 h-4 text-slate-400 mt-0.5" />
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                {article.category}
              </span>
              {article.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-slate-100 text-slate-700 text-xs rounded-full"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
