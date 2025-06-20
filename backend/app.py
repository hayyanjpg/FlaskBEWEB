# backend/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, User, MahasiswaProfile, Application # Mengimpor objek db dan model dari database.py
from werkzeug.utils import secure_filename # Untuk mengamankan nama file yang diunggah
import os
import datetime
from functools import wraps # Digunakan untuk membuat decorator 'login_required' berfungsi dengan benar

# Inisialisasi Flask App
# Tentukan folder templates dan static secara eksplisit agar Flask tahu lokasinya
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# --- Konfigurasi Aplikasi Flask ---
app.config['SECRET_KEY'] = 'your_very_strong_secret_key_here_ganti_ini_dengan_kuat' # GANTI DENGAN KUNCI ACAK YANG KUAT!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kominfo_magang.db' # Konfigurasi database SQLite
app.config['UPLOAD_FOLDER'] = 'backend/static/uploads' # Lokasi penyimpanan file yang diunggah
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Batas ukuran file: 16 MB

# Pastikan folder upload ada, jika tidak, buatlah
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inisialisasi database dengan aplikasi Flask
db.init_app(app)

# --- Decorator Helper untuk Otentikasi dan Otorisasi ---
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn) # Mempertahankan metadata fungsi asli (penting untuk Flask CLI dan debugging)
        def decorated_view(*args, **kwargs):
            # Cek apakah user_id ada di sesi (sudah login)
            if 'user_id' not in session:
                flash('Anda harus login terlebih dahulu.', 'warning')
                return redirect(url_for('login'))
            
            # Ambil objek user dari database berdasarkan user_id di sesi
            user = User.query.get(session['user_id'])
            
            # Jika user tidak ditemukan (mungkin sesi usang atau data dihapus)
            if not user:
                session.pop('user_id', None) # Hapus sesi yang tidak valid
                flash('Sesi tidak valid, silakan login kembali.', 'warning')
                return redirect(url_for('login'))
            
            # Cek role jika ditentukan (misal: @login_required(role='admin'))
            if role and user.role != role:
                flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
                # Arahkan pengguna ke dashboard sesuai rolenya jika tidak diizinkan
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            
            # Jika semua cek lolos, jalankan fungsi asli
            return fn(user, *args, **kwargs)
        return decorated_view
    return wrapper

# --- ROUTES APLIKASI ---

# Route Halaman Utama
@app.route('/')
def index():
    return render_template('index.html')

# Route Pendaftaran Akun Baru
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

        # Cek apakah username atau email sudah terdaftar
        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            flash('Username sudah digunakan.', 'danger')
            return redirect(url_for('register'))

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('register'))

        # Buat user baru dengan role 'mahasiswa'
        new_user = User(username=username, email=email, role='mahasiswa')
        new_user.set_password(password) # Enkripsi password
        db.session.add(new_user)
        db.session.commit() # Simpan user ke database

        # Buat profil mahasiswa kosong yang terkait dengan user baru
        new_profile = MahasiswaProfile(user_id=new_user.id)
        db.session.add(new_profile)
        db.session.commit() # Simpan profil ke database

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        # Verifikasi password
        if user and user.check_password(password):
            session['user_id'] = user.id # Simpan ID user di sesi
            session['role'] = user.role # Simpan role user di sesi
            flash(f'Selamat datang, {user.username}!', 'success')
            # Arahkan ke dashboard yang sesuai dengan role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Username atau kata sandi salah.', 'danger')
    return render_template('login.html')

# Route Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None) # Hapus user_id dari sesi
    session.pop('role', None)    # Hapus role dari sesi
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

# --- ROUTES UNTUK MAHASISWA (ROLE: 'mahasiswa') ---

# Dashboard Mahasiswa
@app.route('/dashboard/mahasiswa')
@login_required(role='mahasiswa') # Hanya bisa diakses oleh user dengan role 'mahasiswa' yang sudah login
def user_dashboard(user): # Objek user dikirimkan oleh decorator
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first() # Ambil profil mahasiswa
    applications = Application.query.filter_by(user_id=user.id).order_by(Application.applied_date.desc()).all() # Ambil semua lamaran mahasiswa
    return render_template('dashboard_user.html', user=user, profile=profile, applications=applications)

# Edit Profil Mahasiswa
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required(role='mahasiswa')
def edit_profile(user):
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first()
    # Ini memastikan profil selalu ada (walaupun kosong)
    if not profile:
        profile = MahasiswaProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.nim = request.form.get('nim')
        profile.university = request.form.get('university')
        profile.major = request.form.get('major')
        
        # Penanganan IPK dengan konversi ke float
        try:
            profile.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else None
        except ValueError:
            profile.gpa = None # Set None jika input tidak valid
            flash('Format IPK tidak valid. Harap masukkan angka (misal: 3.50).', 'warning')

        profile.phone_number = request.form.get('phone_number')
        profile.address = request.form.get('address')

        # Handle unggahan file (CV, Surat Pengantar, Transkrip Nilai)
        files_to_upload = {
            'cv_file': 'cv_path',
            'surat_pengantar_file': 'surat_pengantar_path',
            'transkrip_nilai_file': 'transkrip_nilai_path'
        }

        for file_key, path_attr in files_to_upload.items():
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename != '': # Cek apakah file benar-benar diunggah
                    # Validasi tipe file harus PDF
                    if not file.filename.lower().endswith('.pdf'):
                        flash(f'File {file_key.replace("_file", "").replace("_", " ").upper()} harus dalam format PDF.', 'danger')
                        continue # Lanjutkan ke file berikutnya tanpa menyimpan file ini

                    # Amankan nama file dan simpan
                    filename = secure_filename(f"{user.username}_{file_key}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    setattr(profile, path_attr, filename) # Simpan path file di database

        db.session.commit()
        flash('Profil berhasil diperbarui!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('edit_profile.html', user=user, profile=profile)

# Ajukan Lamaran Magang
@app.route('/apply', methods=['GET', 'POST'])
@login_required(role='mahasiswa')
def apply_magang(user):
    profile = MahasiswaProfile.query.filter_by(user_id=user.id).first()

    # Validasi bahwa profil lengkap dan dokumen sudah diunggah sebelum bisa melamar
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

        # Validasi input tidak boleh kosong
        if not preferred_division or not start_date_str or not end_date_str:
            flash('Harap lengkapi semua bidang yang wajib diisi.', 'danger')
            return render_template('apply_form.html', user=user)

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Validasi tanggal
            if start_date >= end_date:
                flash('Tanggal mulai harus lebih awal dari tanggal selesai.', 'danger')
                return render_template('apply_form.html', user=user)
            
            if start_date < datetime.date.today():
                flash('Tanggal mulai tidak boleh di masa lalu.', 'danger')
                return render_template('apply_form.html', user=user)

        except ValueError:
            flash('Format tanggal tidak valid. Gunakan format YYYY-MM-DD.', 'danger')
            return render_template('apply_form.html', user=user)

        # Buat objek aplikasi baru dan simpan ke database
        new_application = Application(
            user_id=user.id,
            preferred_division=preferred_division,
            start_date=start_date,
            end_date=end_date,
            status='Pending' # Status awal saat pertama kali melamar
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Aplikasi magang Anda berhasil dikirim! Anda dapat melihat statusnya di dashboard.', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('apply_form.html', user=user)

# --- ROUTES UNTUK ADMIN (ROLE: 'admin') ---

# Dashboard Admin
@app.route('/dashboard/admin')
@login_required(role='admin') # Hanya bisa diakses oleh user dengan role 'admin'
def admin_dashboard(user):
    # Ambil semua aplikasi magang, diurutkan dari yang terbaru
    all_applications = Application.query.order_by(Application.applied_date.desc()).all()
    
    # Ambil semua user (bisa juga difilter hanya mahasiswa jika perlu)
    all_users = User.query.all()
    
    # Buat list untuk menggabungkan data aplikasi dengan profil user
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

# Detail Aplikasi Magang (untuk Admin)
@app.route('/admin/application/<int:app_id>/detail', methods=['GET', 'POST'])
@login_required(role='admin')
def application_detail(user, app_id):
    # Ambil data aplikasi, jika tidak ditemukan akan menghasilkan 404
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

# --- Perintah CLI Flask untuk Inisialisasi Database ---
@app.cli.command('init-db')
def init_db_command():
    """Menghapus data yang ada dan membuat tabel baru.
    Juga membuat user admin default."""
    with app.app_context():
        db.drop_all() # Hapus semua tabel yang sudah ada (HATI-HATI: Ini akan menghapus semua data!)
        db.create_all() # Buat semua tabel sesuai model yang didefinisikan
        
        # Buat user admin awal
        admin_user = User(username='admin_kominfo', email='admin@kominfo.go.id', role='admin')
        admin_user.set_password('adminpass123') # GANTI PASSWORD INI SEGERA SETELAH SETUP!
        db.session.add(admin_user)
        db.session.commit()
        print('Database berhasil diinisialisasi dan user admin default dibuat (username: admin_kominfo, password: adminpass123).')
        print('*** PENTING: Segera ganti password admin setelah login pertama kali! ***')

# --- Menjalankan Aplikasi Flask ---
if __name__ == '__main__':
    # Saat skrip ini dijalankan langsung, buat tabel database jika belum ada.
    # Namun, `flask init-db` lebih disarankan untuk kontrol penuh saat inisialisasi awal.
    with app.app_context():
        db.create_all()
    app.run(debug=True) # Aktifkan mode debug untuk pengembangan (fitur auto-reload)