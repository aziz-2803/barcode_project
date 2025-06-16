from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='PORT Yönetim Sistemi')
    dark_mode = db.Column(db.Boolean, default=False)
    bakim_yaklasma_gunu = db.Column(db.Integer, default=7)  # ✅ تمت الإضافة هنا

class Parca(db.Model):
    __tablename__ = 'parcalar'

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    ekipman_turu = db.Column(db.String(100), nullable=False)
    model_adi = db.Column(db.String(100), nullable=False)
    konum = db.Column(db.String(100), nullable=False)
    durum = db.Column(db.String(50), nullable=False)
    bir_sonraki_bakim = db.Column(db.Date, nullable=True)
    son_bakim_tarihi = db.Column(db.Date, nullable=True)
    bakim_dongusu = db.Column(db.String(50), nullable=True)
    bakim_durum = db.Column(db.String(50), nullable=True)  # ✅ تمت إضافته
    notlar = db.Column(db.Text, nullable=True)              # ✅ تمت إضافته
    kisa_aciklama = db.Column(db.Text, nullable=True)
    yuk_kapasitesi = db.Column(db.String(50), nullable=True)
    sorumlu_kisi = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة مع سجل الصيانة
    bakim_kayitlari = db.relationship('BakimKaydi', backref='parca', lazy=True)

class BakimKaydi(db.Model):
    __tablename__ = 'bakim_kaydi'

    id = db.Column(db.Integer, primary_key=True)
    parca_id = db.Column(db.Integer, db.ForeignKey('parcalar.id'), nullable=False)
    tarih = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    aciklama = db.Column(db.Text, nullable=True)
    teknisyen = db.Column(db.String(100), nullable=True)
