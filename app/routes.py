from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Parca, User, Settings
from . import db
import pandas as pd
import io

main = Blueprint('main', __name__)

def parse_dongu(text):
    if not text:
        return None
    text = text.lower()
    if 'gün' in text:
        return lambda d: d + relativedelta(days=int(text.split()[0]))
    elif 'hafta' in text:
        return lambda d: d + relativedelta(weeks=int(text.split()[0]))
    elif 'ay' in text:
        return lambda d: d + relativedelta(months=int(text.split()[0]))
    elif 'yıl' in text:
        return lambda d: d + relativedelta(years=int(text.split()[0]))
    return None

# ======== Dashboard ========
@main.route('/')
@login_required
def dashboard():
    parcalar = Parca.query.all()
    hazir = Parca.query.filter_by(durum='Kullanıma hazır').count()
    bakım = Parca.query.filter_by(durum='Bakım Gerekli').count()
    arizali = Parca.query.filter_by(durum='Arızalı').count()

    bakim_yaklasan_sayisi = 0
    today = datetime.today().date()

    for parca in parcalar:
        parca.bakim_durum = parca.durum
        if parca.son_bakim_tarihi and parca.bakim_dongusu:
            hesapla = parse_dongu(parca.bakim_dongusu)
            if hesapla:
                sonraki = hesapla(parca.son_bakim_tarihi)
                if sonraki and (sonraki - today).days <= 7:
                    parca.bakim_durum = "Bakım Yaklaşan"
                    bakim_yaklasan_sayisi += 1

    return render_template('dashboard.html',
        parcalar=parcalar,
        hazir=hazir,
        bakım=bakım,
        arizali=arizali,
        bakim_yaklasanlar=bakim_yaklasan_sayisi
    )

# ======== Malzemeler ========
@main.route('/materials')
@login_required
def materials():
    parcalar = Parca.query.all()
    return render_template('materials.html', parcalar=parcalar)

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
        son_bakim_tarihi = request.form.get('son_bakim_tarihi')
        bakim_dongusu = request.form.get('bakim_dongusu')
        durum = request.form['durum']
        kisa_aciklama = request.form.get('kisa_aciklama')
        yuk_kapasitesi = request.form.get('yuk_kapasitesi')
        sorumlu_kisi = request.form.get('sorumlu_kisi')

        kod_taban = ekipman_turu.upper().replace(" ", "")
        mevcut_sayisi = Parca.query.filter(Parca.barcode.like(f"{kod_taban}-%")).count() + 1
        barcode = f"{kod_taban}-{mevcut_sayisi:03d}"

        def parse_date(val):
            try:
                return datetime.strptime(val, '%Y-%m-%d').date() if val else None
            except:
                return None

        yeni_parca = Parca(
            barcode=barcode,
            model_adi=model_adi,
            ekipman_turu=ekipman_turu,
            konum=konum,
            durum=durum,
            bir_sonraki_bakim=parse_date(bir_sonraki_bakim),
            son_bakim_tarihi=parse_date(son_bakim_tarihi),
            bakim_dongusu=bakim_dongusu,
            kisa_aciklama=kisa_aciklama,
            yuk_kapasitesi=yuk_kapasitesi,
            sorumlu_kisi=sorumlu_kisi
        )

        db.session.add(yeni_parca)
        db.session.commit()
        flash("Yeni parça başarıyla eklendi.", "success")
        return redirect(url_for('main.materials'))

    return render_template('yeni.html')

# ======== Parça Detay ========
@main.route('/detail/<int:parca_id>', methods=['GET', 'POST'])
@login_required
def detail(parca_id):
    parca = Parca.query.get_or_404(parca_id)
    if request.method == 'POST':
        parca.konum = request.form['konum']
        parca.durum = request.form['durum']
        parca.kisa_aciklama = request.form['kisa_aciklama']
        parca.bir_sonraki_bakim = datetime.strptime(request.form.get('bir_sonraki_bakim'), '%Y-%m-%d') if request.form.get('bir_sonraki_bakim') else None
        parca.son_bakim_tarihi = datetime.strptime(request.form.get('son_bakim_tarihi'), '%Y-%m-%d') if request.form.get('son_bakim_tarihi') else None
        parca.bakim_dongusu = request.form.get('bakim_dongusu')
        db.session.commit()
        flash('Parça başarıyla güncellendi.', 'success')
        return redirect(url_for('main.detail', parca_id=parca.id))
    return render_template('detail.html', parca=parca)

# ======== Parça Düzenle ========
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
        parca.bir_sonraki_bakim = datetime.strptime(request.form.get('bir_sonraki_bakim'), '%Y-%m-%d') if request.form.get('bir_sonraki_bakim') else None
        parca.son_bakim_tarihi = datetime.strptime(request.form.get('son_bakim_tarihi'), '%Y-%m-%d') if request.form.get('son_bakim_tarihi') else None
        parca.bakim_dongusu = request.form.get('bakim_dongusu')
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
    return redirect(url_for('main.materials'))

# ======== Kullanıcılar ========
@main.route('/users')
@login_required
def users():
    if current_user.role != 'Admin':
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@main.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Admin':
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Kullanıcı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.users'))
    return render_template('add_user.html')

@main.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Admin':
        flash('Bu işlemi yapma yetkiniz yok.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Kendi hesabınızı silemezsiniz!', 'warning')
        return redirect(url_for('main.users'))
    db.session.delete(user)
    db.session.commit()
    flash('Kullanıcı silindi.', 'success')
    return redirect(url_for('main.users'))

# ======== Ayarlar ========
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    setting = Settings.query.first()
    if request.method == 'POST':
        if 'dark_mode' in request.form:
            setting.dark_mode = True
        else:
            setting.dark_mode = False

        if 'old_password' in request.form and 'new_password' in request.form:
            old = request.form['old_password']
            new = request.form['new_password']
            confirm = request.form['confirm_password']
            if new != confirm:
                flash('Yeni şifreler uyuşmuyor.', 'danger')
            elif not check_password_hash(current_user.password, old):
                flash('Eski şifre hatalı.', 'danger')
            else:
                current_user.password = generate_password_hash(new)
                db.session.commit()
                flash('Şifre başarıyla değiştirildi.', 'success')
        elif 'site_name' in request.form:
            setting.site_name = request.form['site_name']
            db.session.commit()
            flash('Site adı güncellendi.', 'success')

        return redirect(url_for('main.settings'))

    return render_template('settings.html', setting=setting)

# ======== Çıkış ========
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# ======== Excel Dışa Aktar ========
@main.route('/export_excel')
@login_required
def export_excel():
    parcalar = Parca.query.all()
    data = []
    for parca in parcalar:
        data.append({
            "Barkod": parca.barcode,
            "Model Adı": parca.model_adi,
            "Ekipman Türü": parca.ekipman_turu,
            "Konum": parca.konum,
            "Durum": parca.durum,
            "Bir Sonraki Bakım": parca.bir_sonraki_bakim.strftime('%Y-%m-%d') if parca.bir_sonraki_bakim else '',
            "Son Bakım Tarihi": parca.son_bakim_tarihi.strftime('%Y-%m-%d') if parca.son_bakim_tarihi else '',
            "Bakım Döngüsü": parca.bakim_dongusu or '',
            "Yük Kapasitesi": parca.yuk_kapasitesi,
            "Sorumlu Kişi": parca.sorumlu_kisi,
            "Açıklama / Not": parca.kisa_aciklama
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Parçalar')

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=malzemeler.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
