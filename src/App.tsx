import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { CourseGrid } from './components/CourseGrid';
import { CourseDetail } from './components/CourseDetail';
import { useDatabase } from './hooks/useDatabase';
import { Course, Comment, Rating } from './types';

function App() {
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [ratings, setRatings] = useState<Rating[]>([]);
  
  const { 
    isReady, 
    getCourses, 
    getCourseComments, 
    getCourseRatings, 
    addComment, 
    addRating 
  } = useDatabase();

  useEffect(() => {
    if (isReady) {
      setCourses(getCourses());
    }
  }, [isReady, getCourses]);

  useEffect(() => {
    if (selectedCourse) {
      setComments(getCourseComments(selectedCourse.id));
      setRatings(getCourseRatings(selectedCourse.id));
    }
  }, [selectedCourse, getCourseComments, getCourseRatings]);

  const handleCourseClick = (course: Course) => {
    setSelectedCourse(course);
  };

  const handleBack = () => {
    setSelectedCourse(null);
  };

  const handleAddComment = (content: string) => {
    if (selectedCourse) {
      // Demo user ID = 3 (Mike Wilson)
      addComment(selectedCourse.id, 3, content);
      setComments(getCourseComments(selectedCourse.id));
    }
  };

  const handleAddRating = (rating: number, review: string) => {
    if (selectedCourse) {
      // Demo user ID = 3 (Mike Wilson)
      addRating(selectedCourse.id, 3, rating, review);
      setRatings(getCourseRatings(selectedCourse.id));
      // Update courses to reflect new rating
      setCourses(getCourses());
    }
  };

  if (!isReady) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Database yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedCourse ? (
          <CourseDetail
            course={selectedCourse}
            comments={comments}
            ratings={ratings}
            onBack={handleBack}
            onAddComment={handleAddComment}
            onAddRating={handleAddRating}
          />
        ) : (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                Onlayn Kurslar Platformasi
              </h1>
              <p className="text-gray-600">
                Professional darajadagi kurslar bilan o'z bilimingizni oshiring
              </p>
            </div>
            
            <CourseGrid courses={courses} onCourseClick={handleCourseClick} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;