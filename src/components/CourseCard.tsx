import React from 'react';
import { Star, Users, Clock } from 'lucide-react';
import { Course } from '../types';

interface CourseCardProps {
  course: Course;
  onClick: () => void;
}

export const CourseCard: React.FC<CourseCardProps> = ({ course, onClick }) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('uz-UZ').format(price) + ' so\'m';
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <div 
      className="card hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
      onClick={onClick}
    >
      <div className="relative overflow-hidden rounded-lg mb-4">
        <img
          src={course.image_url}
          alt={course.title}
          className="w-full h-48 object-cover transition-transform duration-300 hover:scale-105"
        />
        <div className="absolute top-2 right-2 bg-white px-2 py-1 rounded-full text-sm font-medium">
          {course.level}
        </div>
      </div>
      
      <h3 className="text-xl font-bold text-gray-800 mb-2 line-clamp-2">
        {course.title}
      </h3>
      
      <p className="text-gray-600 mb-3 line-clamp-2">
        {course.description}
      </p>
      
      <div className="flex items-center mb-3 text-sm text-gray-500">
        <span className="font-medium">{course.instructor_name}</span>
      </div>
      
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-1">
          {renderStars(course.rating)}
          <span className="text-sm text-gray-600 ml-1">
            ({course.rating.toFixed(1)})
          </span>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1" />
            {course.students_count}
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {course.duration}
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-blue-600">
          {formatPrice(course.price)}
        </span>
        <button className="btn-primary">
          Kursni ko'rish
        </button>
      </div>
    </div>
  );
};