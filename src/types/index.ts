export interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  role: 'student' | 'instructor' | 'admin';
  created_at: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  instructor_id: number;
  instructor_name: string;
  price: number;
  duration: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  image_url: string;
  rating: number;
  students_count: number;
  created_at: string;
}

export interface Lesson {
  id: number;
  course_id: number;
  title: string;
  content: string;
  video_url?: string;
  duration: string;
  order_index: number;
}

export interface Comment {
  id: number;
  course_id: number;
  user_id: number;
  user_name: string;
  user_avatar?: string;
  content: string;
  created_at: string;
}

export interface Rating {
  id: number;
  course_id: number;
  user_id: number;
  user_name: string;
  rating: number;
  review: string;
  created_at: string;
}

export interface Enrollment {
  id: number;
  user_id: number;
  course_id: number;
  progress: number;
  enrolled_at: string;
}