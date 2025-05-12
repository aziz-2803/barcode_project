from app import db
from app.models import Parca
from flask import Flask
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE parcalar ADD COLUMN son_bakim_tarihi DATE"))
            print("✔️ son_bakim_tarihi eklendi.")
        except Exception as e:
            print("⚠️ son_bakim_tarihi zaten var veya hata:", e)

        try:
            conn.execute(text("ALTER TABLE parcalar ADD COLUMN bakim_dongusu TEXT"))
            print("✔️ bakim_dongusu eklendi.")
        except Exception as e:
            print("⚠️ bakim_dongusu zaten var veya hata:", e)
