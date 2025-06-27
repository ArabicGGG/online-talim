import { useState, useEffect } from 'react';
import { initDatabase, getDatabase } from '../database/db';
import { Course, User, Comment, Rating } from '../types';

export const useDatabase = () => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    initDatabase().then(() => {
      setIsReady(true);
    });
  }, []);

  const getCourses = (): Course[] => {
    if (!isReady) return [];
    const db = getDatabase();
    const stmt = db.prepare(`
      SELECT c.*, u.name as instructor_name,
             COALESCE(AVG(r.rating), 0) as rating,
             COUNT(DISTINCT e.user_id) as students_count
      FROM courses c
      LEFT JOIN users u ON c.instructor_id = u.id
      LEFT JOIN ratings r ON c.id = r.course_id
      LEFT JOIN enrollments e ON c.id = e.course_id
      GROUP BY c.id
    `);
    const courses = [];
    while (stmt.step()) {
      courses.push(stmt.getAsObject());
    }
    stmt.free();
    return courses as Course[];
  };

  const getCourseById = (id: number): Course | null => {
    if (!isReady) return null;
    const db = getDatabase();
    const stmt = db.prepare(`
      SELECT c.*, u.name as instructor_name,
             COALESCE(AVG(r.rating), 0) as rating,
             COUNT(DISTINCT e.user_id) as students_count
      FROM courses c
      LEFT JOIN users u ON c.instructor_id = u.id
      LEFT JOIN ratings r ON c.id = r.course_id
      LEFT JOIN enrollments e ON c.id = e.course_id
      WHERE c.id = ?
      GROUP BY c.id
    `);
    stmt.bind([id]);
    const course = stmt.step() ? stmt.getAsObject() : null;
    stmt.free();
    return course as Course | null;
  };

  const getCourseComments = (courseId: number): Comment[] => {
    if (!isReady) return [];
    const db = getDatabase();
    const stmt = db.prepare(`
      SELECT c.*, u.name as user_name, u.avatar as user_avatar
      FROM comments c
      JOIN users u ON c.user_id = u.id
      WHERE c.course_id = ?
      ORDER BY c.created_at DESC
    `);
    stmt.bind([courseId]);
    const comments = [];
    while (stmt.step()) {
      comments.push(stmt.getAsObject());
    }
    stmt.free();
    return comments as Comment[];
  };

  const getCourseRatings = (courseId: number): Rating[] => {
    if (!isReady) return [];
    const db = getDatabase();
    const stmt = db.prepare(`
      SELECT r.*, u.name as user_name
      FROM ratings r
      JOIN users u ON r.user_id = u.id
      WHERE r.course_id = ?
      ORDER BY r.created_at DESC
    `);
    stmt.bind([courseId]);
    const ratings = [];
    while (stmt.step()) {
      ratings.push(stmt.getAsObject());
    }
    stmt.free();
    return ratings as Rating[];
  };

  const addComment = (courseId: number, userId: number, content: string) => {
    if (!isReady) return;
    const db = getDatabase();
    db.run('INSERT INTO comments (course_id, user_id, content) VALUES (?, ?, ?)', 
           [courseId, userId, content]);
  };

  const addRating = (courseId: number, userId: number, rating: number, review: string) => {
    if (!isReady) return;
    const db = getDatabase();
    db.run('INSERT OR REPLACE INTO ratings (course_id, user_id, rating, review) VALUES (?, ?, ?, ?)', 
           [courseId, userId, rating, review]);
  };

  return {
    isReady,
    getCourses,
    getCourseById,
    getCourseComments,
    getCourseRatings,
    addComment,
    addRating
  };
};