# backend/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, User, MahasiswaProfile, Application
from werkzeug.utils import secure_filename
import os
import datetime
from functools import wraps
import re # Diperlukan untuk validasi password

# Inisialisasi Flask App
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# --- Konfigurasi Aplikasi Flask ---
app.config['SECRET_KEY'] = 'your_very_strong_secret_key_here_ganti_ini_dengan_kuat' # GANTI DENGAN KUNCI ACAK YANG KUAT!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kominfo_magang.db' # Konfigurasi database SQLite

# Menggunakan os.path.join dan app.root_path untuk path UPLOAD_FOLDER yang lebih robust
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Batas ukuran file: 16 MB

# Pastikan folder upload ada, jika tidak, buatlah
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inisialisasi database dengan aplikasi Flask
db.init_app(app)

# --- Decorator Helper untuk Otentikasi dan Otorisasi ---
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                flash('Anda harus login terlebih dahulu.', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user:
                session.pop('user_id', None)
                flash('Sesi tidak valid, silakan login kembali.', 'warning')
                return redirect(url_for('login'))
            if role and user.role != role:
                flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            return fn(user, *args, **kwargs)
        return decorated_view
    return wrapper

# --- ROUTES APLIKASI ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Konfirmasi kata sandi tidak cocok!', 'danger')
            return redirect(url_for('register'))

        # === VALIDASI PASSWORD BARU ===
        # Minimal 10 karakter
        if len(password) < 10:
            flash('Kata sandi minimal harus 10 karakter.', 'danger')
            return redirect(url_for('register'))
        
        # Minimal 1 karakter khusus (misal: @, #, $, %, ^, &, *, !, ~, ?, .)
        if not re.search(r'[!@#$%^&*()_+{}\[\]:;"\'<>,.?/~`]', password):
            flash('Kata sandi harus mengandung setidaknya satu karakter khusus (contoh: @, #, $).', 'danger')
            return redirect(url_for('register'))
        
        # Minimal 1 angka
        if not re.search(r'\d', password):
            flash('Kata sandi harus mengandung setidaknya satu angka.', 'danger')
            return redirect(url_for('register'))
        # ==============================

        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            flash('Username sudah digunakan.', 'danger')
            return redirect(url_for('register'))

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, role='mahasiswa')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        new_profile = MahasiswaProfile(user_id=new_user.id)
        db.session.add(new_profile)
        db.session.commit()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Selamat datang, {user.username}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Username atau kata sandi salah.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard/mahasiswa')
@login_required(role='mahasiswa')
def user_dashboard(user):
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first()
    applications = Application.query.filter_by(user_id=user.id).order_by(Application.applied_date.desc()).all()
    return render_template('dashboard_user.html', user=user, profile=profile, applications=applications)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required(role='mahasiswa')
def edit_profile(user):
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = MahasiswaProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.nim = request.form.get('nim')
        profile.university = request.form.get('university')
        profile.major = request.form.get('major')
        
        try:
            profile.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else None
        except ValueError:
            profile.gpa = None
            flash('Format IPK tidak valid. Harap masukkan angka (misal: 3.50).', 'warning')

        profile.phone_number = request.form.get('phone_number')
        profile.address = request.form.get('address')

        files_to_upload = {
            'cv_file': 'cv_path',
            'surat_pengantar_file': 'surat_pengantar_path',
            'transkrip_nilai_file': 'transkrip_nilai_path'
        }

        for file_key, path_attr in files_to_upload.items():
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename != '':
                    if not file.filename.lower().endswith('.pdf'):
                        flash(f'File {file_key.replace("_file", "").replace("_", " ").upper()} harus dalam format PDF.', 'danger')
                        continue

                    filename = secure_filename(f"{user.username}_{file_key}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    setattr(profile, path_attr, filename)

        db.session.commit()
        flash('Profil berhasil diperbarui!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('edit_profile.html', user=user, profile=profile)

@app.route('/apply', methods=['GET', 'POST'])
@login_required(role='mahasiswa')
def apply_magang(user):
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first()

    if not profile or not profile.full_name or not profile.nim or not profile.university or not profile.major:
        flash('Lengkapi data pribadi (Nama, NIM, Universitas, Jurusan) di profil Anda sebelum melamar magang.', 'warning')
        return redirect(url_for('edit_profile'))
    if not profile.cv_path or not profile.surat_pengantar_path or not profile.transkrip_nilai_path:
        flash('Unggah semua dokumen wajib (CV, Surat Pengantar, Transkrip Nilai) di profil Anda sebelum melamar magang.', 'warning')
        return redirect(url_for('edit_profile'))

    if request.method == 'POST':
        preferred_division = request.form.get('preferred_division')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not preferred_division or not start_date_str or not end_date_str:
            flash('Harap lengkapi semua bidang yang wajib diisi.', 'danger')
            return render_template('apply_form.html', user=user)

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date >= end_date:
                flash('Tanggal mulai harus lebih awal dari tanggal selesai.', 'danger')
                return render_template('apply_form.html', user=user)
            
            if start_date < datetime.date.today():
                flash('Tanggal mulai tidak boleh di masa lalu.', 'danger')
                return render_template('apply_form.html', user=user)

        except ValueError:
            flash('Format tanggal tidak valid. Gunakan format YYYY-MM-DD.', 'danger')
            return render_template('apply_form.html', user=user)

        new_application = Application(
            user_id=user.id,
            preferred_division=preferred_division,
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Aplikasi magang Anda berhasil dikirim! Anda dapat melihat statusnya di dashboard.', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('apply_form.html', user=user)

@app.route('/dashboard/admin')
@login_required(role='admin')
def admin_dashboard(user):
    all_applications = Application.query.order_by(Application.applied_date.desc()).all()
    all_users = User.query.all()
    
    applications_data = []
    for app in all_applications:
        user_data = User.query.get(app.user_id)
        profile_data = MahasiswaProfile.query.filter_by(user_id=app.user_id).first()
        applications_data.append({
            'application': app,
            'user': user_data,
            'profile': profile_data
        })
    
    return render_template('dashboard_admin.html',
                           user=user,
                           applications_data=applications_data,
                           all_users=all_users)

@app.route('/admin/application/<int:app_id>/detail', methods=['GET', 'POST'])
@login_required(role='admin')
def application_detail(user, app_id):
    application = Application.query.get_or_404(app_id)
    applicant_user = User.query.get_or_404(application.user_id)
    applicant_profile = MahasiswaProfile.query.filter_by(user_id=applicant_user.id).first()

    if request.method == 'POST':
        new_status = request.form.get('status')
        admin_notes = request.form.get('admin_notes')
        
        application.status = new_status
        application.admin_notes = admin_notes
        db.session.commit()
        flash(f'Status aplikasi {applicant_user.username} berhasil diperbarui menjadi {new_status}.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_application_detail.html',
                           user=user,
                           application=application,
                           applicant_user=applicant_user,
                           applicant_profile=applicant_profile)

@app.cli.command('init-db')
def init_db_command():
    """Menghapus data yang ada dan membuat tabel baru.
    Juga membuat user admin default."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        admin_user = User(username='admin_kominfo', email='admin@kominfo.go.id', role='admin')
        admin_user.set_password('adminpass123')
        db.session.add(admin_user)
        db.session.commit()
        print('Database berhasil diinisialisasi dan user admin default dibuat (username: admin_kominfo, password: adminpass123).')
        print('*** PENTING: Segera ganti password admin setelah login pertama kali! ***')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)