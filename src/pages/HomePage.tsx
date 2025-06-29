import React, { useEffect, useState } from 'react';
import api from '@/lib/api';

interface Course {
  id: number;
  title: string;
  description: string;
  instructor_name: string;
  price: number;
  duration: string;
  level: string;
  category: string;
  image_url: string;
  rating: number;
  students_count: number;
  created_at: string;
}

export default function HomePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await api.get<Course[]>('/api/courses');
        setCourses(response.data);
      } catch (err: any) {
        setError('Kurslarni yuklashda xatolik yuz berdi.');
        console.error('Error fetching courses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Kurslar yuklanmoqda...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Onlayn Kurslar</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-2">{course.title}</h2>
            <p className="text-gray-600 mb-2">O'qituvchi: {course.instructor_name}</p>
            <p className="text-gray-700 mb-4">{course.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-lg font-bold text-blue-600">{course.price} UZS</span>
              <span className="text-sm text-gray-500">{course.duration}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
