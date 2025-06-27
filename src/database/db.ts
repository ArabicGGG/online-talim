import initSqlJs from 'sql.js';

let db: any = null;

export const initDatabase = async () => {
  if (db) return db;
  
  const SQL = await initSqlJs({
    locateFile: file => `https://sql.js.org/dist/${file}`
  });
  
  db = new SQL.Database();
  
  // Create tables
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      avatar TEXT,
      role TEXT DEFAULT 'student',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS courses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT NOT NULL,
      instructor_id INTEGER,
      price REAL DEFAULT 0,
      duration TEXT,
      level TEXT DEFAULT 'beginner',
      image_url TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (instructor_id) REFERENCES users (id)
    );
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS lessons (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_id INTEGER,
      title TEXT NOT NULL,
      content TEXT,
      video_url TEXT,
      duration TEXT,
      order_index INTEGER DEFAULT 0,
      FOREIGN KEY (course_id) REFERENCES courses (id)
    );
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_id INTEGER,
      user_id INTEGER,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (course_id) REFERENCES courses (id),
      FOREIGN KEY (user_id) REFERENCES users (id)
    );
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_id INTEGER,
      user_id INTEGER,
      rating INTEGER CHECK (rating >= 1 AND rating <= 5),
      review TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (course_id) REFERENCES courses (id),
      FOREIGN KEY (user_id) REFERENCES users (id),
      UNIQUE(course_id, user_id)
    );
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS enrollments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      course_id INTEGER,
      progress REAL DEFAULT 0,
      enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users (id),
      FOREIGN KEY (course_id) REFERENCES courses (id),
      UNIQUE(user_id, course_id)
    );
  `);
  
  // Insert sample data
  insertSampleData();
  
  return db;
};

const insertSampleData = () => {
  // Sample users
  db.run(`INSERT OR IGNORE INTO users (id, name, email, role) VALUES 
    (1, 'John Smith', 'john@example.com', 'instructor'),
    (2, 'Sarah Johnson', 'sarah@example.com', 'instructor'),
    (3, 'Mike Wilson', 'mike@example.com', 'student'),
    (4, 'Anna Davis', 'anna@example.com', 'student')
  `);
  
  // Sample courses
  db.run(`INSERT OR IGNORE INTO courses (id, title, description, instructor_id, price, duration, level, image_url) VALUES 
    (1, 'React.js Asoslari', 'React.js ni noldan o''rganish uchun to''liq kurs. Zamonaviy web development texnologiyalari bilan tanishing.', 1, 299000, '8 soat', 'beginner', 'https://images.pexels.com/photos/11035380/pexels-photo-11035380.jpeg?auto=compress&cs=tinysrgb&w=500'),
    (2, 'JavaScript Advanced', 'JavaScript ning murakkab mavzulari: async/await, closures, prototypes va boshqalar.', 1, 399000, '12 soat', 'advanced', 'https://images.pexels.com/photos/270348/pexels-photo-270348.jpeg?auto=compress&cs=tinysrgb&w=500'),
    (3, 'Python Data Science', 'Python yordamida ma''lumotlar tahlili va machine learning asoslari.', 2, 499000, '15 soat', 'intermediate', 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=500'),
    (4, 'Web Design Fundamentals', 'HTML, CSS va responsive design asoslari. Chiroyli veb-saytlar yaratishni o''rganing.', 2, 199000, '6 soat', 'beginner', 'https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=500')
  `);
  
  // Sample lessons
  db.run(`INSERT OR IGNORE INTO lessons (course_id, title, content, duration, order_index) VALUES 
    (1, 'React.js nima?', 'React.js haqida umumiy ma''lumot va uning afzalliklari', '30 min', 1),
    (1, 'Komponentlar yaratish', 'React komponentlarini yaratish va ishlatish', '45 min', 2),
    (1, 'State va Props', 'React da state va props bilan ishlash', '40 min', 3),
    (2, 'Async/Await', 'JavaScript da asinxron dasturlash', '50 min', 1),
    (2, 'Closures va Scope', 'JavaScript da closures va scope tushunchalari', '35 min', 2)
  `);
  
  // Sample comments
  db.run(`INSERT OR IGNORE INTO comments (course_id, user_id, content) VALUES 
    (1, 3, 'Juda yaxshi kurs! Hamma narsa tushunarli tarzda tushuntirilgan.'),
    (1, 4, 'Instructor juda professional. Tavsiya qilaman!'),
    (2, 3, 'Murakkab mavzular lekin yaxshi tushuntirilgan.')
  `);
  
  // Sample ratings
  db.run(`INSERT OR IGNORE INTO ratings (course_id, user_id, rating, review) VALUES 
    (1, 3, 5, 'Ajoyib kurs! Hamma narsani tushundim.'),
    (1, 4, 4, 'Yaxshi kurs, lekin ba''zi qismlar qiyinroq edi.'),
    (2, 3, 5, 'Professional darajadagi kurs!')
  `);
};

export const getDatabase = () => db;