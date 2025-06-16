from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Parca, User, Settings
from . import db
import pandas as pd
import io

import os
import barcode as barcode_module
from barcode.writer import ImageWriter

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
    setting = Settings.query.first()
    uyari_gun = setting.bakim_yaklasma_gunu if setting and setting.bakim_yaklasma_gunu else 30

    parcalar = Parca.query.all()
    hazir = 0
    bakım = 0
    arizali = 0
    bakim_yaklasan_sayisi = 0
    today = datetime.today().date()

    for parca in parcalar:
        parca.bakim_durum = None
        if parca.son_bakim_tarihi and parca.bakim_dongusu:
            try:
                ay = int(parca.bakim_dongusu)
                sonraki = parca.son_bakim_tarihi + relativedelta(months=ay)
                parca.bir_sonraki_bakim = sonraki
                kalan_gun = (sonraki - today).days

                if kalan_gun < 0:
                    parca.durum = "Bakım Gerekli"
                elif kalan_gun <= uyari_gun and parca.durum == "Kullanıma hazır":
                    parca.bakim_durum = "Bakım Yaklaşan"
            except:
                pass

        if parca.durum == "Kullanıma hazır":
            hazir += 1
        elif parca.durum == "Bakım Gerekli":
            bakım += 1
        elif parca.durum == "Arızalı":
            arizali += 1

        if parca.bakim_durum == "Bakım Yaklaşan":
            bakim_yaklasan_sayisi += 1

    return render_template(
        'dashboard.html',
        parcalar=parcalar,
        hazir=hazir,
        bakım=bakım,
        arizali=arizali,
        bakim_yaklasanlar=bakim_yaklasan_sayisi
    )

# ======== Malzemeler ========
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

        # ✅ Barkod görselini oluştur ve kaydet
        barcode_path = os.path.join("generated_barcodes", f"{barcode}.png")
        barcode_img = barcode_module.Code128(barcode, writer=ImageWriter())
        barcode_img.save(barcode_path)

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
        return redirect(url_for('main.malzeme_listesi'))

    return render_template('yeni.html')


# ======== Parça Detay ========
@main.route('/detail/<int:parca_id>')
@login_required
def detail(parca_id):
    parca = Parca.query.get_or_404(parca_id)
    today = datetime.today().date()

    # جلب إعدادات النظام
    setting = Settings.query.first()
    uyari_gun = setting.bakim_yaklasma_gunu if setting and setting.bakim_yaklasma_gunu is not None else 30

    # حساب bir_sonraki_bakim تلقائيًا من son_bakim_tarihi + bakim_dongusu
    if parca.son_bakim_tarihi and parca.bakim_dongusu:
        try:
            ay = int(parca.bakim_dongusu)
            parca.bir_sonraki_bakim = parca.son_bakim_tarihi + relativedelta(months=ay)
        except:
            parca.bir_sonraki_bakim = None
    else:
        parca.bir_sonraki_bakim = None

    # تحديد الحالة تلقائيًا (إلا إذا كانت Arızalı)
    if parca.durum != 'Arızalı' and parca.bir_sonraki_bakim:
        kalan = (parca.bir_sonraki_bakim - today).days
        if kalan < 0:
            parca.durum = 'Bakım Gerekli'
        elif kalan <= uyari_gun:
            parca.durum = 'Bakım Yaklaşan'
        else:
            parca.durum = 'Kullanıma hazır'

    return render_template('detail.html', parca=parca, today=today)

# ======== Parça Düzenle ========
@main.route('/parca/<int:parca_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(parca_id):
    parca = Parca.query.get_or_404(parca_id)

    if request.method == 'POST':
        parca.barcode = request.form['barcode']
        parca.ekipman_turu = request.form['ekipman_turu']
        parca.model_adi = request.form['model_adi']
        parca.konum = request.form['konum']
        parca.sorumlu_kisi = request.form['sorumlu_kisi']
        parca.kisa_aciklama = request.form['kisa_aciklama']
        parca.yuk_kapasitesi = request.form['yuk_kapasitesi']

        # التاريخ
        son_bakim_str = request.form['son_bakim_tarihi']
        parca.son_bakim_tarihi = datetime.strptime(son_bakim_str, '%Y-%m-%d').date() if son_bakim_str else None

        # دورة الصيانة
        bakim_dongusu = request.form.get('bakim_dongusu')
        parca.bakim_dongusu = int(bakim_dongusu) if bakim_dongusu else None

        # حساب التاريخ القادم
        if parca.son_bakim_tarihi and parca.bakim_dongusu:
            parca.bir_sonraki_bakim = parca.son_bakim_tarihi + relativedelta(months=+parca.bakim_dongusu)
        else:
            parca.bir_sonraki_bakim = None

        # حالة العطل
        if 'arizali_mi' in request.form:
            parca.durum = 'Arızalı'
        else:
            # حساب الحالة تلقائيًا
            bugun = datetime.now().date()
            if parca.bir_sonraki_bakim:
                kalan = (parca.bir_sonraki_bakim - bugun).days
                if kalan < 0:
                    parca.durum = 'Bakım Gerekli'
                elif kalan <= 7:
                    parca.durum = 'Kullanıma hazır'  # جاهزة ولكن قريبة أيضًا
                else:
                    parca.durum = 'Kullanıma hazır'
            else:
                parca.durum = 'Kullanıma hazır'

        db.session.commit()
        flash("Parça başarıyla güncellendi.", "success")
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
        # الوضع الداكن
        setting.dark_mode = 'dark_mode' in request.form

        # تغيير كلمة المرور
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

        # اسم الموقع وعدد أيام التنبيه
        elif 'site_name' in request.form or 'bakim_yaklasma_gunu' in request.form:
            if 'site_name' in request.form:
                setting.site_name = request.form['site_name']
            if 'bakim_yaklasma_gunu' in request.form:
                try:
                    setting.bakim_yaklasma_gunu = int(request.form['bakim_yaklasma_gunu'])
                except ValueError:
                    setting.bakim_yaklasma_gunu = 30
            db.session.commit()
            flash('Ayarlar güncellendi.', 'success')

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
            "Yük Kapasitesi": parca.yuk_kapasitesi or '',
            "Sorumlu Kişi": parca.sorumlu_kisi or '',
            "Açıklama / Not": parca.kisa_aciklama or ''
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Parçalar')
        workbook = writer.book
        worksheet = writer.sheets['Parçalar']

        # تنسيق العناوين
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'middle',
            'align': 'center',
            'fg_color': '#D9D9D9',
            'border': 1
        })

        # تطبيق التنسيق على رؤوس الأعمدة
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            column_width = max(df[value].astype(str).map(len).max(), len(value)) + 4
            worksheet.set_column(col_num, col_num, column_width)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=Ekipmanlar.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

