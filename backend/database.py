# backend/database.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Inisialisasi objek SQLAlchemy, yang akan dihubungkan ke aplikasi Flask nanti
db = SQLAlchemy()

# Model untuk tabel User (pengguna, bisa mahasiswa atau admin)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='mahasiswa') # Peran pengguna: 'mahasiswa' atau 'admin'
    is_active = db.Column(db.Boolean, default=True) # Status akun aktif/tidak aktif

    # Relasi one-to-one dengan profil mahasiswa
    # 'backref' menciptakan atribut 'user' pada MahasiswaProfile
    # 'uselist=False' menandakan hubungan satu-ke-satu (satu user punya satu profil)
    mahasiswa_profile = db.relationship('MahasiswaProfile', backref='user', uselist=False)
    
    # Relasi one-to-many dengan aplikasi magang
    # 'lazy=True' berarti data aplikasi akan dimuat saat diakses
    applications = db.relationship('Application', backref='user', lazy=True)

    # Metode untuk mengenkripsi password saat menyimpan ke database
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Metode untuk memverifikasi password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Representasi objek User (untuk debugging)
    def __repr__(self):
        return f'<User {self.username}>'

# Model untuk tabel MahasiswaProfile (detail profil mahasiswa)
class MahasiswaProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False) # Foreign Key ke tabel User
    full_name = db.Column(db.String(100), nullable=True)
    nim = db.Column(db.String(50), unique=True, nullable=True)
    university = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    gpa = db.Column(db.Float, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    
    # Path ke lokasi file yang diunggah
    cv_path = db.Column(db.String(200), nullable=True)
    surat_pengantar_path = db.Column(db.String(200), nullable=True)
    transkrip_nilai_path = db.Column(db.String(200), nullable=True)
    # Anda bisa menambahkan kolom lain untuk dokumen jika diperlukan

    # Representasi objek MahasiswaProfile
    def __repr__(self):
        return f'<MahasiswaProfile {self.full_name}>'

# Model untuk tabel Application (lamaran magang mahasiswa)
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign Key ke tabel User
    applied_date = db.Column(db.DateTime, default=datetime.datetime.utcnow) # Tanggal dan waktu lamaran
    status = db.Column(db.String(50), default='Pending') # Status lamaran (Pending, Reviewed, Accepted, Rejected, Interview)
    preferred_division = db.Column(db.String(100), nullable=True) # Divisi yang diminati
    start_date = db.Column(db.Date, nullable=True) # Tanggal mulai magang yang diinginkan
    end_date = db.Column(db.Date, nullable=True) # Tanggal selesai magang yang diinginkan
    admin_notes = db.Column(db.Text, nullable=True) # Catatan internal untuk admin

    # Representasi objek Application
    def __repr__(self):
        return f'<Application {self.id} - User: {self.user_id} - Status: {self.status}>'

# Catatan: Jika di masa depan ada lowongan spesifik, Anda bisa mengaktifkan model ini
# class InternshipVacancy(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     requirements = db.Column(db.Text, nullable=False)
#     quota = db.Column(db.Integer, nullable=True)
#     department = db.Column(db.String(100), nullable=True)
#     deadline = db.Column(db.Date, nullable=True)
#     is_active = db.Column(db.Boolean, default=True)
#     applications = db.relationship('Application', backref='vacancy', lazy=True)