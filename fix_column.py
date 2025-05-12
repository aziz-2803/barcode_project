from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE parcalar ADD COLUMN son_bakim_tarihi TEXT"))
        db.session.commit()
        print("✅ Kolon başarıyla eklendi.")
    except Exception as e:
        print("❌ Hata:", e)
