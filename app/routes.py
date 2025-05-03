from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import Parca, User, Settings
from . import db

main = Blueprint('main', __name__)

# ======== Dashboard ========
@main.route('/')
@login_required
def dashboard():
    parcalar = Parca.query.all()
    hazir = Parca.query.filter_by(durum='Kullanıma hazır').count()
    bakım = Parca.query.filter_by(durum='Bakım Gerekli').count()
    arizali = Parca.query.filter_by(durum='Arızalı').count()
    return render_template('dashboard.html',
                           parcalar=parcalar,
                           hazir=hazir,
                           bakım=bakım,
                           arizali=arizali)

# ======== Malzeme Listesi ========
@main.route('/malzemeler')
@login_required
def malzeme_listesi():
    parcalar = Parca.query.all()
    return render_template('malzemeler.html', parcalar=parcalar)

# ======== Yeni Parça Ekle ========
@main.route('/parca/add', methods=['GET', 'POST'])
@login_required
def add_parca():
    if request.method == 'POST':
        ekipman_turu = request.form['ekipman_turu']
        model_adi = request.form['model_adi']
        konum = request.form['konum']
        bir_sonraki_bakim = request.form.get('bir_sonraki_bakim')
        durum = request.form['durum']
        kisa_aciklama = request.form.get('kisa_aciklama')
        yuk_kapasitesi = request.form.get('yuk_kapasitesi')
        sorumlu_kisi = request.form.get('sorumlu_kisi')

        kod_taban = ekipman_turu.upper().replace(" ", "")
        mevcut_sayisi = Parca.query.filter(Parca.barcode.like(f"{kod_taban}-%")).count() + 1
        barcode = f"{kod_taban}-{mevcut_sayisi:03d}"

        bir_sonraki_bakim_tarihi = None
        if bir_sonraki_bakim:
            try:
                bir_sonraki_bakim_tarihi = datetime.strptime(bir_sonraki_bakim, '%Y-%m-%d').date()
            except:
                flash("Geçersiz tarih formatı.", "danger")
                return redirect(url_for('main.add_parca'))

        yeni_parca = Parca(
            barcode=barcode,
            model_adi=model_adi,
            ekipman_turu=ekipman_turu,
            konum=konum,
            durum=durum,
            bir_sonraki_bakim=bir_sonraki_bakim_tarihi,
            kisa_aciklama=kisa_aciklama,
            yuk_kapasitesi=yuk_kapasitesi,
            sorumlu_kisi=sorumlu_kisi
        )

        db.session.add(yeni_parca)
        db.session.commit()
        flash("Yeni parça başarıyla eklendi.", "success")
        return redirect(url_for('main.malzeme_listesi'))

    return render_template('yeni.html')

# ======== Parça Detay ve Basit Güncelleme ========
@main.route('/detail/<int:parca_id>', methods=['GET', 'POST'])
@login_required
def detail(parca_id):
    parca = Parca.query.get_or_404(parca_id)
    if request.method == 'POST':
        parca.konum = request.form['konum']
        parca.durum = request.form['durum']
        bir_sonraki_bakim_str = request.form.get('bir_sonraki_bakim')
        if bir_sonraki_bakim_str:
            parca.bir_sonraki_bakim = datetime.strptime(bir_sonraki_bakim_str, '%Y-%m-%d').date()
        else:
            parca.bir_sonraki_bakim = None
        parca.kisa_aciklama = request.form['kisa_aciklama']
        db.session.commit()
        flash('Parça başarıyla güncellendi.', 'success')
        return redirect(url_for('main.malzeme_listesi'))
    return render_template('detail.html', parca=parca)

# ======== Parça Tam Güncelleme ========
@main.route('/edit/<int:parca_id>', methods=['GET', 'POST'])
@login_required
def edit(parca_id):
    parca = Parca.query.get_or_404(parca_id)

    if request.method == 'POST':
        parca.barcode = request.form['barcode']
        parca.ekipman_turu = request.form['ekipman_turu']
        parca.model_adi = request.form['model_adi']
        parca.konum = request.form['konum']
        parca.durum = request.form['durum']

        bir_sonraki_bakim = request.form.get('bir_sonraki_bakim')
        if bir_sonraki_bakim:
            try:
                parca.bir_sonraki_bakim = datetime.strptime(bir_sonraki_bakim, '%Y-%m-%d').date()
            except:
                flash("Tarih formatı geçersiz.", "danger")

        parca.kisa_aciklama = request.form['kisa_aciklama']
        parca.yuk_kapasitesi = request.form['yuk_kapasitesi']
        parca.sorumlu_kisi = request.form['sorumlu_kisi']

        db.session.commit()
        flash("Malzeme başarıyla güncellendi.", "success")
        return redirect(url_for('main.detail', parca_id=parca.id))

    return render_template('edit.html', parca=parca)

# ======== Parça Sil ========
@main.route('/parca/delete/<int:parca_id>', methods=['POST'])
@login_required
def delete_parca(parca_id):
    parca = Parca.query.get_or_404(parca_id)
    db.session.delete(parca)
    db.session.commit()
    flash('Parça başarıyla silindi.', 'success')
    return redirect(url_for('main.malzeme_listesi'))

# ======== Kullanıcılar ========
@main.route('/users')
@login_required
def users():
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('main.dashboard'))
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@main.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('تم إنشاء المستخدم بنجاح.', 'success')
        return redirect(url_for('main.users'))
    return render_template('add_user.html')

@main.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Admin':
        flash('ليس لديك صلاحية الوصول إلى هذه العملية.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الحالي!', 'warning')
        return redirect(url_for('main.users'))
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم.', 'success')
    return redirect(url_for('main.users'))

# ======== Ayarlar ========
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting = Settings.query.first()
    if request.method == 'POST':
        if 'old_password' in request.form and 'new_password' in request.form:
            old = request.form['old_password']
            new = request.form['new_password']
            confirm = request.form['confirm_password']
            if new != confirm:
                flash('كلمات المرور الجديدة غير متطابقة.', 'danger')
            elif not check_password_hash(current_user.password, old):
                flash('كلمة المرور القديمة غير صحيحة.', 'danger')
            else:
                current_user.password = generate_password_hash(new)
                db.session.commit()
                flash('تم تغيير كلمة المرور بنجاح.', 'success')
        else:
            setting.site_name = request.form['site_name']
            db.session.commit()
            flash('تم تحديث الإعدادات العامة.', 'success')
        return redirect(url_for('main.settings'))
    return render_template('settings.html', setting=setting)

# ======== Çıkış ========
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
