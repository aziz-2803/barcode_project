from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE settings ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE'))
        db.session.commit()
        print("✅ Kolon başarıyla eklendi.")
    except Exception as e:
        print("❌ Hata:", e)
