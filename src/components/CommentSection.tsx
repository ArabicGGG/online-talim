import React, { useState } from 'react';
import { MessageCircle, Send } from 'lucide-react';
import { Comment } from '../types';

interface CommentSectionProps {
  comments: Comment[];
  onAddComment: (content: string) => void;
}

export const CommentSection: React.FC<CommentSectionProps> = ({ comments, onAddComment }) => {
  const [newComment, setNewComment] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      onAddComment(newComment.trim());
      setNewComment('');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div>
      <h3 className="text-xl font-semibold mb-6 flex items-center">
        <MessageCircle className="w-5 h-5 mr-2" />
        Izohlar ({comments.length})
      </h3>

      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex space-x-4">
          <div className="flex-1">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Izoh qoldiring..."
              className="input-field resize-none h-20"
              required
            />
          </div>
          <button
            type="submit"
            className="btn-primary px-6 h-20 flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>

      <div className="space-y-6">
        {comments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Hali izohlar yo'q. Birinchi bo'lib izoh qoldiring!</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="border-b border-gray-100 pb-6 last:border-b-0">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                  {comment.user_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-medium text-gray-800">{comment.user_name}</h4>
                    <span className="text-sm text-gray-500">{formatDate(comment.created_at)}</span>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{comment.content}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};