import React, { useState } from 'react';
import { ArrowLeft, Star, Users, Clock, Play } from 'lucide-react';
import { Course, Comment, Rating } from '../types';
import { CommentSection } from './CommentSection';
import { RatingSection } from './RatingSection';

interface CourseDetailProps {
  course: Course;
  comments: Comment[];
  ratings: Rating[];
  onBack: () => void;
  onAddComment: (content: string) => void;
  onAddRating: (rating: number, review: string) => void;
}

export const CourseDetail: React.FC<CourseDetailProps> = ({
  course,
  comments,
  ratings,
  onBack,
  onAddComment,
  onAddRating
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'comments' | 'ratings'>('overview');

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('uz-UZ').format(price) + ' so\'m';
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${
          i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <div className="max-w-6xl mx-auto">
      <button
        onClick={onBack}
        className="flex items-center text-blue-600 hover:text-blue-700 mb-6 transition-colors"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Orqaga qaytish
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="relative overflow-hidden rounded-lg mb-6">
            <img
              src={course.image_url}
              alt={course.title}
              className="w-full h-64 object-cover"
            />
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
              <button className="bg-white bg-opacity-20 backdrop-blur-sm rounded-full p-4 hover:bg-opacity-30 transition-all">
                <Play className="w-8 h-8 text-white" />
              </button>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-gray-800 mb-4">{course.title}</h1>
          
          <div className="flex items-center space-x-6 mb-6 text-sm text-gray-600">
            <div className="flex items-center">
              {renderStars(course.rating)}
              <span className="ml-2">({course.rating.toFixed(1)})</span>
            </div>
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-1" />
              {course.students_count} talaba
            </div>
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              {course.duration}
            </div>
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
              {course.level}
            </span>
          </div>

          <div className="border-b border-gray-200 mb-6">
            <nav className="flex space-x-8">
              {[
                { key: 'overview', label: 'Umumiy ma\'lumot' },
                { key: 'comments', label: `Izohlar (${comments.length})` },
                { key: 'ratings', label: `Baholar (${ratings.length})` }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="min-h-96">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Kurs haqida</h3>
                <p className="text-gray-700 leading-relaxed mb-6">{course.description}</p>
                
                <h3 className="text-xl font-semibold mb-4">Siz nimani o'rganasiz</h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Zamonaviy web development texnologiyalari
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Amaliy loyihalar ustida ishlash
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Professional darajadagi kod yozish
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Real loyihalarda qo'llash
                  </li>
                </ul>
              </div>
            )}

            {activeTab === 'comments' && (
              <CommentSection comments={comments} onAddComment={onAddComment} />
            )}

            {activeTab === 'ratings' && (
              <RatingSection ratings={ratings} onAddRating={onAddRating} />
            )}
          </div>
        </div>

        <div className="lg:col-span-1">
          <div className="card sticky top-6">
            <div className="text-center mb-6">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {formatPrice(course.price)}
              </div>
              <p className="text-gray-600">Bir martalik to'lov</p>
            </div>

            <button className="btn-primary w-full mb-4 py-3 text-lg">
              Kursni sotib olish
            </button>

            <button className="btn-secondary w-full mb-6">
              Bepul darsni ko'rish
            </button>

            <div className="space-y-4 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Instructor:</span>
                <span className="font-medium">{course.instructor_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Davomiyligi:</span>
                <span className="font-medium">{course.duration}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Daraja:</span>
                <span className="font-medium capitalize">{course.level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Talabalar:</span>
                <span className="font-medium">{course.students_count}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};