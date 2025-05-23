from app import create_app, db
from app.models import Parca
from sqlalchemy import text
from datetime import datetime

app = create_app()

def convert_date(value):
    # ✅ إذا كانت القيمة None نتركها كما هي
    if value is None:
        return None

    # ✅ إذا كانت القيمة datetime نعيدها مباشرة
    if isinstance(value, datetime):
        return value.date()

    # ✅ إذا كانت نصًا نحاول تحويله
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            print("❌ Geçersiz tarih:", value)
            return None

    # ❌ في أي حالة أخرى نطبع تحذير ونتجاهلها
    print("⚠️ Bilinmeyen veri tipi:", value, type(value))
    return None

def fix_dates():
    with app.app_context():
        result = db.session.execute(text("SELECT id, son_bakim_tarihi, bir_sonraki_bakim, created_at FROM parcalar"))
        rows = result.fetchall()

        for row in rows:
            parca_id = row[0]
            son_bakim = convert_date(row[1])
            bir_sonraki = convert_date(row[2])
            created = convert_date(row[3])

            parca = db.session.get(Parca, parca_id)
            if parca:
                parca.son_bakim_tarihi = son_bakim
                parca.bir_sonraki_bakim = bir_sonraki
                parca.created_at = created

        db.session.commit()
        print("✔️ Tüm tarih alanları başarıyla güncellendi.")

if __name__ == '__main__':
    fix_dates()
