import React from 'react';
import { Course } from '../types';
import { CourseCard } from './CourseCard';

interface CourseGridProps {
  courses: Course[];
  onCourseClick: (course: Course) => void;
}

export const CourseGrid: React.FC<CourseGridProps> = ({ courses, onCourseClick }) => {
  if (courses.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Kurslar yuklanmoqda...</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          course={course}
          onClick={() => onCourseClick(course)}
        />
      ))}
    </div>
  );
};