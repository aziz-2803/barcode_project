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

class Parca(db.Model):
    __tablename__ = 'parcalar'

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    ekipman_turu = db.Column(db.String(100), nullable=False)
    model_adi = db.Column(db.String(100), nullable=False)
    konum = db.Column(db.String(100), nullable=False)
    durum = db.Column(db.String(50), nullable=False)
    bir_sonraki_bakim = db.Column(db.Date, nullable=True)
    kisa_aciklama = db.Column(db.Text, nullable=True)
    yuk_kapasitesi = db.Column(db.String(50), nullable=True)
    sorumlu_kisi = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
