
from app import app, db, init_db
   
with app.app_context():
        print("Initializing database...")
        init_db()
print("Database initialized successfully!")