import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { Rating } from '../types';

interface RatingSectionProps {
  ratings: Rating[];
  onAddRating: (rating: number, review: string) => void;
}

export const RatingSection: React.FC<RatingSectionProps> = ({ ratings, onAddRating }) => {
  const [newRating, setNewRating] = useState(0);
  const [newReview, setNewReview] = useState('');
  const [hoveredRating, setHoveredRating] = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newRating > 0 && newReview.trim()) {
      onAddRating(newRating, newReview.trim());
      setNewRating(0);
      setNewReview('');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const renderStars = (rating: number, interactive = false) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${
          interactive ? 'cursor-pointer' : ''
        } ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
        onClick={interactive ? () => setNewRating(i + 1) : undefined}
        onMouseEnter={interactive ? () => setHoveredRating(i + 1) : undefined}
        onMouseLeave={interactive ? () => setHoveredRating(0) : undefined}
      />
    ));
  };

  const averageRating = ratings.length > 0 
    ? ratings.reduce((sum, rating) => sum + rating.rating, 0) / ratings.length 
    : 0;

  return (
    <div>
      <h3 className="text-xl font-semibold mb-6 flex items-center">
        <Star className="w-5 h-5 mr-2" />
        Baholar ({ratings.length})
      </h3>

      {ratings.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-800 mb-2">
              {averageRating.toFixed(1)}
            </div>
            <div className="flex justify-center mb-2">
              {renderStars(Math.round(averageRating))}
            </div>
            <p className="text-gray-600">{ratings.length} ta baholash</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-4">Kursni baholang</h4>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Baho bering:
          </label>
          <div className="flex space-x-1">
            {renderStars(hoveredRating || newRating, true)}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sharh qoldiring:
          </label>
          <textarea
            value={newReview}
            onChange={(e) => setNewReview(e.target.value)}
            placeholder="Kurs haqida fikringizni yozing..."
            className="input-field resize-none h-24"
            required
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={newRating === 0 || !newReview.trim()}
        >
          Baholash yuborish
        </button>
      </form>

      <div className="space-y-6">
        {ratings.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Star className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Hali baholar yo'q. Birinchi bo'lib baholang!</p>
          </div>
        ) : (
          ratings.map((rating) => (
            <div key={rating.id} className="border-b border-gray-100 pb-6 last:border-b-0">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-medium">
                  {rating.user_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-medium text-gray-800">{rating.user_name}</h4>
                    <div className="flex">
                      {renderStars(rating.rating)}
                    </div>
                    <span className="text-sm text-gray-500">{formatDate(rating.created_at)}</span>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{rating.review}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};