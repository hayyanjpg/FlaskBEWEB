# backend/database.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='mahasiswa') # 'mahasiswa' or 'admin'
    is_active = db.Column(db.Boolean, default=True) # For future features like account activation

    mahasiswa_profile = db.relationship('MahasiswaProfile', backref='user', uselist=False)
    applications = db.relationship('Application', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class MahasiswaProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    nim = db.Column(db.String(50), unique=True, nullable=True)
    university = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    gpa = db.Column(db.Float, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    cv_path = db.Column(db.String(200), nullable=True)
    surat_pengantar_path = db.Column(db.String(200), nullable=True)
    transkrip_nilai_path = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<MahasiswaProfile {self.full_name}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applied_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(50), default='Pending') # e.g., 'Pending', 'Reviewed', 'Accepted', 'Rejected', 'Interview'
    preferred_division = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Application {self.id} - User: {self.user_id} - Status: {self.status}>'