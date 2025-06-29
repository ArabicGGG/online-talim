from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY muhit o'zgaruvchisi o'rnatilmagan. Iltimos, .env faylini yarating yoki uni muhit o'zgaruvchisi sifatida o'rnating.")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("DATABASE_URL muhit o'zgaruvchisi o'rnatilmagan. Iltimos, .env faylini yarating yoki uni muhit o'zgaruvchisi sifatida o'rnating.")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app, supports_credentials=True)

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'course_images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # student or instructor
    avatar = db.Column(db.String(200))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='instructor', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(500))
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, default=0)
    duration = db.Column(db.String(50))
    level = db.Column(db.String(20), default='beginner')
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    video_preview_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='course', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='course', lazy=True, cascade='all, delete-orphan')
    
    @property
    def average_rating(self):
        if self.ratings:
            return sum(r.rating for r in self.ratings) / len(self.ratings)
        return 0
    
    @property
    def students_count(self):
        return len(self.enrollments)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    duration = db.Column(db.String(20))
    order_index = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('course_id', 'user_id'),)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress = db.Column(db.Float, default=0)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id'),)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id'),)

# Helper functions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder, allowed_extensions):
    if file and allowed_file(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = str(int(datetime.now().timestamp()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        file.save(file_path)
        return f"/static/uploads/{folder}/{filename}"
    return None

# Routes
@app.route('/')
def index():
    courses = Course.query.filter_by(is_published=True).all()
    return render_template('index.html', courses=courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            role = data.get('role', 'student')
            
            # Validation
            if not name or len(name) < 2:
                return jsonify({'error': 'Ism kamida 2 ta belgidan iborat bo\'lishi kerak'}), 400
            
            if not email or '@' not in email:
                return jsonify({'error': 'To\'g\'ri email manzilini kiriting'}), 400
                
            if not password or len(password) < 6:
                return jsonify({'error': 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak'}), 400
            
            # Check for existing email
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Bu email allaqachon ro\'yxatdan o\'tgan'}), 400
            
            # Check for existing name (case insensitive)
            if User.query.filter(db.func.lower(User.name) == name.lower()).first():
                return jsonify({'error': 'Bu ism allaqachon ishlatilgan. Boshqa ism tanlang'}), 400
            
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(name=name, email=email, password_hash=password_hash, role=role)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            return jsonify({'success': True, 'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }})
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Ro'yxatdan o'tishda xatolik: {e}")
            return jsonify({'error': 'Ro\'yxatdan o\'tishda xatolik yuz berdi'}), 500
    
    return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email va parolni kiriting'}), 400
            
            user = User.query.filter_by(email=email).first()
            
            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)
                return jsonify({'success': True, 'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                }})
            
            return jsonify({'error': 'Noto\'g\'ri email yoki parol'}), 401
            
        except Exception as e:
            app.logger.error(f"Kirishda xatolik: {e}")
            return jsonify({'error': 'Kirishda xatolik yuz berdi'}), 500
    
    return render_template('auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    if request.method == 'GET':
        return jsonify({
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'role': current_user.role,
            'avatar': current_user.avatar,
            'bio': current_user.bio,
            'phone': current_user.phone,
            'location': current_user.location,
            'website': current_user.website
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            new_name = data.get('name', current_user.name).strip()
            
            # Check if name is being changed and if it's already taken
            if new_name.lower() != current_user.name.lower():
                existing_user = User.query.filter(
                    db.func.lower(User.name) == new_name.lower(),
                    User.id != current_user.id
                ).first()
                if existing_user:
                    return jsonify({'error': 'Bu ism allaqachon ishlatilgan. Boshqa ism tanlang'}), 400
            
            current_user.name = new_name
            current_user.bio = data.get('bio', current_user.bio)
            current_user.phone = data.get('phone', current_user.phone)
            current_user.location = data.get('location', current_user.location)
            current_user.website = data.get('website', current_user.website)
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Profilni yangilashda xatolik yuz berdi'}), 500

@app.route('/api/upload/avatar', methods=['POST'])
@login_required
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({'error': 'Fayl tanlanmagan'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': 'Fayl tanlanmagan'}), 400
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        avatar_url = save_uploaded_file(file, 'avatars', allowed_extensions)
        
        if avatar_url:
            current_user.avatar = avatar_url
            db.session.commit()
            return jsonify({'success': True, 'avatar_url': avatar_url})
        else:
            return jsonify({'error': 'Noto\'g\'ri fayl formati. PNG, JPG, JPEG, GIF fayllarini yuklang'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Rasm yuklashda xatolik yuz berdi'}), 500

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    user_data = {
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role,
        'avatar': current_user.avatar
    }
    return render_template('cart.html', cart_items=cart_items, current_user_data=user_data)

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_cart():
    if request.method == 'GET':
        try:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            items = []
            total = 0
            
            cart_items = CartItem.query.filter_by(user_id=current_user.id).options(
                db.joinedload(CartItem.course).joinedload(Course.instructor)
            ).all()
            items = []
            total = 0
            
            for item in cart_items:
                course = item.course
                if course:  # Check if course still exists
                    items.append({
                        'id': item.id,
                        'course': {
                            'id': course.id,
                            'title': course.title,
                            'instructor_name': course.instructor.name,
                            'price': course.price,
                            'image_url': course.image_url,
                            'rating': course.average_rating,
                            'duration': course.duration
                        }
                    })
                    total += course.price
            
            return jsonify({
                'items': items,
                'total': total,
                'count': len(items)
            })
        except Exception as e:
            return jsonify({'error': 'Savatchani yuklashda xatolik yuz berdi'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            course_id = data.get('course_id')
            
            if not course_id:
                return jsonify({'error': 'Kurs ID kiritilmagan'}), 400
            
            # Check if course exists
            course = Course.query.get(course_id)
            if not course:
                return jsonify({'error': 'Kurs topilmadi'}), 404
            
            # Check if already enrolled
            enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
            if enrollment:
                return jsonify({'error': 'Siz allaqachon bu kursga yozilgansiz'}), 400
            
            # Check if already in cart
            existing_item = CartItem.query.filter_by(user_id=current_user.id, course_id=course_id).first()
            if existing_item:
                return jsonify({'error': 'Kurs allaqachon savatchada'}), 400
            
            cart_item = CartItem(user_id=current_user.id, course_id=course_id)
            db.session.add(cart_item)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Kurs savatchaga qo\'shildi!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Savatchaga qo\'shishda xatolik yuz berdi'}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            item_id = data.get('item_id')
            
            if not item_id:
                return jsonify({'error': 'Element ID kiritilmagan'}), 400
            
            cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                return jsonify({'success': True})
            
            return jsonify({'error': 'Element topilmadi'}), 404
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Elementni o\'chirishda xatolik yuz berdi'}), 500

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            return jsonify({'error': 'Savatcha bo\'sh'}), 400
        
        # Create enrollments for all cart items
        enrolled_courses = []
        for item in cart_items:
            course = Course.query.get(item.course_id)
            if course:
                # Check if not already enrolled
                existing_enrollment = Enrollment.query.filter_by(
                    user_id=current_user.id, 
                    course_id=item.course_id
                ).first()
                
                if not existing_enrollment:
                    enrollment = Enrollment(user_id=current_user.id, course_id=item.course_id)
                    db.session.add(enrollment)
                    enrolled_courses.append(course.title)
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{len(enrolled_courses)} ta kurs muvaffaqiyatli sotib olindi!',
            'enrolled_courses': enrolled_courses
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Sotib olishda xatolik yuz berdi'}), 500

@app.route('/api/courses')
def api_courses():
    try:
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        
        query = Course.query.filter_by(is_published=True).options(db.joinedload(Course.instructor))
        
        if search:
            query = query.filter(
                db.or_(
                    Course.title.contains(search),
                    Course.description.contains(search),
                    Course.short_description.contains(search)
                )
            )
        
        if category and category != 'all':
            query = query.filter(Course.category == category)
        
        courses = query.all()
        
        return jsonify([{
            'id': course.id,
            'title': course.title,
            'description': course.short_description or course.description[:200],
            'instructor_name': course.instructor.name,
            'price': course.price,
            'duration': course.duration,
            'level': course.level,
            'category': course.category,
            'image_url': course.image_url,
            'rating': course.average_rating,
            'students_count': course.students_count,
            'created_at': course.created_at.isoformat()
        } for course in courses])
        
    except Exception as e:
        return jsonify({'error': 'Kurslarni yuklashda xatolik yuz berdi'}), 500

@app.route('/api/courses/<int:course_id>')
def api_course_detail(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        return jsonify({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'instructor_name': course.instructor.name,
            'instructor_bio': course.instructor.bio,
            'price': course.price,
            'duration': course.duration,
            'level': course.level,
            'category': course.category,
            'image_url': course.image_url,
            'video_preview_url': course.video_preview_url,
            'rating': course.average_rating,
            'students_count': course.students_count,
            'lessons': [{
                'id': lesson.id,
                'title': lesson.title,
                'duration': lesson.duration,
                'is_free': lesson.is_free,
                'video_url': lesson.video_url
            } for lesson in course.lessons],
            'created_at': course.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': 'Kurs ma\'lumotlarini yuklashda xatolik yuz berdi'}), 500

@app.route('/api/courses/<int:course_id>/comments')
def api_course_comments(course_id):
    try:
        comments = Comment.query.filter_by(course_id=course_id).order_by(Comment.created_at.desc()).all()
        return jsonify([{
            'id': comment.id,
            'user_name': comment.user.name,
            'user_avatar': comment.user.avatar,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        } for comment in comments])
    except Exception as e:
        return jsonify({'error': 'Izohlarni yuklashda xatolik yuz berdi'}), 500

@app.route('/api/courses/<int:course_id>/ratings')
def api_course_ratings(course_id):
    try:
        ratings = Rating.query.filter_by(course_id=course_id).order_by(Rating.created_at.desc()).all()
        return jsonify([{
            'id': rating.id,
            'user_name': rating.user.name,
            'rating': rating.rating,
            'review': rating.review,
            'created_at': rating.created_at.isoformat()
        } for rating in ratings])
    except Exception as e:
        return jsonify({'error': 'Baholarni yuklashda xatolik yuz berdi'}), 500

@app.route('/api/courses/<int:course_id>/comments', methods=['POST'])
@login_required
def add_comment(course_id):
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Izoh matnini kiriting'}), 400
        
        if len(content) > 1000:
            return jsonify({'error': 'Izoh juda uzun (maksimal 1000 belgi)'}), 400
        
        course = Course.query.get_or_404(course_id)
        
        comment = Comment(course_id=course_id, user_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Izoh qo\'shishda xatolik yuz berdi'}), 500

@app.route('/api/courses/<int:course_id>/ratings', methods=['POST'])
@login_required
def add_rating(course_id):
    try:
        data = request.get_json()
        rating_value = data.get('rating')
        review = data.get('review', '').strip()
        
        if not rating_value or rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'Baho 1 dan 5 gacha bo\'lishi kerak'}), 400
        
        if not review:
            return jsonify({'error': 'Sharh yozish majburiy'}), 400
        
        if len(review) > 1000:
            return jsonify({'error': 'Sharh juda uzun (maksimal 1000 belgi)'}), 400
        
        course = Course.query.get_or_404(course_id)
        
        # Check if user already rated this course
        existing_rating = Rating.query.filter_by(course_id=course_id, user_id=current_user.id).first()
        
        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.review = review
        else:
            rating = Rating(course_id=course_id, user_id=current_user.id, rating=rating_value, review=review)
            db.session.add(rating)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Baho qo\'shishda xatolik yuz berdi'}), 500

@app.route('/instructor/dashboard')
@login_required
def instructor_dashboard():
    if current_user.role != 'instructor':
        return redirect(url_for('index'))
    
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor_dashboard.html', courses=courses)

@app.route('/instructor/courses/new', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'instructor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Handle form data (multipart/form-data for file uploads)
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            short_description = request.form.get('short_description', '').strip()
            price = float(request.form.get('price', 0))
            duration = request.form.get('duration', '').strip()
            level = request.form.get('level', '')
            category = request.form.get('category', '')
            
            # Validation
            if not all([title, description, price, duration, level, category]):
                return jsonify({'error': 'Barcha majburiy maydonlarni to\'ldiring'}), 400
            
            # Handle course image upload
            image_url = None
            if 'course_image' in request.files:
                file = request.files['course_image']
                if file and file.filename:
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    image_url = save_uploaded_file(file, 'course_images', allowed_extensions)
            
            course = Course(
                title=title,
                description=description,
                short_description=short_description,
                instructor_id=current_user.id,
                price=price,
                duration=duration,
                level=level,
                category=category,
                image_url=image_url,
                is_published=True
            )
            
            db.session.add(course)
            db.session.flush()  # Get course ID
            
            # Handle lessons and videos
            lesson_count = int(request.form.get('lesson_count', 0))
            for i in range(lesson_count):
                lesson_title = request.form.get(f'lesson_title_{i}', '').strip()
                lesson_content = request.form.get(f'lesson_content_{i}', '').strip()
                lesson_duration = request.form.get(f'lesson_duration_{i}', '').strip()
                lesson_is_free = request.form.get(f'lesson_is_free_{i}') == 'true'
                
                if lesson_title:
                    # Handle video upload for this lesson
                    video_url = None
                    video_file_key = f'lesson_video_{i}'
                    if video_file_key in request.files:
                        video_file = request.files[video_file_key]
                        if video_file and video_file.filename:
                            allowed_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
                            video_url = save_uploaded_file(video_file, 'videos', allowed_extensions)
                    
                    lesson = Lesson(
                        course_id=course.id,
                        title=lesson_title,
                        content=lesson_content,
                        duration=lesson_duration,
                        order_index=i + 1,
                        is_free=lesson_is_free,
                        video_url=video_url
                    )
                    db.session.add(lesson)
            
            db.session.commit()
            
            return jsonify({'success': True, 'course_id': course.id})
            
        except ValueError:
            return jsonify({'error': 'Narx raqam bo\'lishi kerak'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Kurs yaratishda xatolik yuz berdi: {str(e)}'}), 500
    
    return render_template('create_course.html')

@app.route('/api/upload/video', methods=['POST'])
@login_required
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'Video fayl tanlanmagan'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'Video fayl tanlanmagan'}), 400
        
        allowed_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
        video_url = save_uploaded_file(file, 'videos', allowed_extensions)
        
        if video_url:
            return jsonify({'success': True, 'video_url': video_url})
        else:
            return jsonify({'error': 'Noto\'g\'ri video formati. MP4, AVI, MOV, WMV, FLV, WEBM fayllarini yuklang'}), 400
            
    except Exception as e:
        return jsonify({'error': 'Video yuklashda xatolik yuz berdi'}), 500

@app.route('/api/user/current')
@login_required
def current_user_info():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role,
        'avatar': current_user.avatar
    })

@app.route('/api/cart/count')
@login_required
def cart_count():
    try:
        count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0})

# Video viewing route
@app.route('/watch/<int:lesson_id>')
@login_required
def watch_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course
    
    # Check if user is enrolled or if lesson is free
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    
    if not lesson.is_free and not enrollment:
        return jsonify({'error': 'Bu darsni ko\'rish uchun kursga yozilishingiz kerak'}), 403
    
    return render_template('watch_lesson.html', lesson=lesson, course=course)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Sahifa topilmadi'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': error.description or 'Noto\'g\'ri so\'rov'}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Server xatosi yuz berdi'}), 500


# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create sample data if no users exist
        if not User.query.first():
            try:
                # Create sample instructor
                instructor_password = bcrypt.generate_password_hash('password123').decode('utf-8')
                instructor = User(
                    name='John Smith',
                    email='instructor@example.com',
                    password_hash=instructor_password,
                    role='instructor',
                    bio='Professional web developer with 10+ years experience',
                    phone='+998901234567',
                    location='Toshkent, O\'zbekiston',
                    website='https://johnsmith.dev'
                )
                
                # Create sample student
                student_password = bcrypt.generate_password_hash('password123').decode('utf-8')
                student = User(
                    name='Sarah Johnson',
                    email='student@example.com',
                    password_hash=student_password,
                    role='student',
                    bio='Aspiring web developer',
                    phone='+998907654321',
                    location='Samarqand, O\'zbekiston'
                )
                
                db.session.add(instructor)
                db.session.add(student)
                db.session.commit()
                
                # Create sample courses
                courses_data = [
                    {
                        'title': 'React.js Asoslari',
                        'description': 'React.js ni noldan o\'rganish uchun to\'liq kurs. Zamonaviy web development texnologiyalari bilan tanishing. Bu kursda siz React komponentlari, state management, hooks va boshqa muhim mavzularni o\'rganasiz.',
                        'short_description': 'React.js ni noldan o\'rganing va zamonaviy web ilovalar yarating',
                        'price': 299000,
                        'duration': '8 soat',
                        'level': 'beginner',
                        'category': 'Web Development',
                        'image_url': 'https://images.pexels.com/photos/11035380/pexels-photo-11035380.jpeg?auto=compress&cs=tinysrgb&w=500',
                        'is_published': True
                    },
                    {
                        'title': 'JavaScript Advanced',
                        'description': 'JavaScript ning murakkab mavzulari: async/await, closures, prototypes va boshqalar. Bu kurs tajribali dasturchilarga mo\'ljallangan.',
                        'short_description': 'JavaScript ning murakkab mavzularini chuqur o\'rganing',
                        'price': 399000,
                        'duration': '12 soat',
                        'level': 'advanced',
                        'category': 'Programming',
                        'image_url': 'https://images.pexels.com/photos/270348/pexels-photo-270348.jpeg?auto=compress&cs=tinysrgb&w=500',
                        'is_published': True
                    },
                    {
                        'title': 'Python Data Science',
                        'description': 'Python yordamida ma\'lumotlar tahlili va machine learning asoslari. Pandas, NumPy, Matplotlib va Scikit-learn kutubxonalari bilan ishlashni o\'rganing.',
                        'short_description': 'Python bilan Data Science va Machine Learning',
                        'price': 499000,
                        'duration': '15 soat',
                        'level': 'intermediate',
                        'category': 'Data Science',
                        'image_url': 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=500',
                        'is_published': True
                    },
                    {
                        'title': 'Web Design Fundamentals',
                        'description': 'HTML, CSS va responsive design asoslari. Chiroyli va zamonaviy veb-saytlar yaratishni o\'rganing. Flexbox, Grid va CSS animatsiyalari.',
                        'short_description': 'Web dizayn asoslari va responsive design',
                        'price': 199000,
                        'duration': '6 soat',
                        'level': 'beginner',
                        'category': 'Design',
                        'image_url': 'https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=500',
                        'is_published': True
                    }
                ]
                
                for course_data in courses_data:
                    course = Course(instructor_id=instructor.id, **course_data)
                    db.session.add(course)
                
                db.session.commit()
                
                # Add sample lessons
                courses = Course.query.all()
                for course in courses:
                    lessons_data = [
                        {'title': f'{course.title} - Kirish', 'duration': '15 min', 'order_index': 1, 'is_free': True},
                        {'title': f'{course.title} - Asosiy qism', 'duration': '45 min', 'order_index': 2, 'is_free': False},
                        {'title': f'{course.title} - Amaliyot', 'duration': '30 min', 'order_index': 3, 'is_free': False},
                        {'title': f'{course.title} - Xulosa', 'duration': '20 min', 'order_index': 4, 'is_free': False}
                    ]
                    
                    for lesson_data in lessons_data:
                        lesson = Lesson(
                            course_id=course.id,
                            title=lesson_data['title'],
                            content=f"Bu {lesson_data['title']} darsi tarkibi",
                            duration=lesson_data['duration'],
                            order_index=lesson_data['order_index'],
                            is_free=lesson_data['is_free']
                        )
                        db.session.add(lesson)
                
                # Add sample comments and ratings
                sample_comments = [
                    {'course_id': 1, 'user_id': 2, 'content': 'Juda yaxshi kurs! Hamma narsa tushunarli tarzda tushuntirilgan.'},
                    {'course_id': 1, 'user_id': 2, 'content': 'Instructor juda professional. Tavsiya qilaman!'},
                    {'course_id': 2, 'user_id': 2, 'content': 'Murakkab mavzular lekin yaxshi tushuntirilgan.'}
                ]
                
                for comment_data in sample_comments:
                    comment = Comment(**comment_data)
                    db.session.add(comment)
                
                sample_ratings = [
                    {'course_id': 1, 'user_id': 2, 'rating': 5, 'review': 'Ajoyib kurs! Hamma narsani tushundim.'},
                    {'course_id': 2, 'user_id': 2, 'rating': 4, 'review': 'Yaxshi kurs, lekin ba\'zi qismlar qiyinroq edi.'},
                    {'course_id': 3, 'user_id': 2, 'rating': 5, 'review': 'Professional darajadagi kurs!'}
                ]
                
                for rating_data in sample_ratings:
                    rating = Rating(**rating_data)
                    db.session.add(rating)
                
                db.session.commit()
                print("Sample data created successfully!")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error creating sample data: {e}")

# Ensure database tables are created on startup if they don't exist
with app.app_context():
    # Check if any table exists (e.g., User table)
    # This is a simple check to avoid recreating tables on every restart
    # For more robust solutions, consider Flask-Migrate
    try:
        db.session.query(User).first()
    except Exception as e:
        print(f"Database tables not found or error: {e}. Initializing database...")
        init_db()
        print("Database initialization attempt completed.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)