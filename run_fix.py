from app import create_app
from app.models import db
from datetime import datetime, date
from sqlalchemy import text  # ✅ مهم

app = create_app()

def convert_to_date_safe(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except:
            return None
    if isinstance(value, int):
        try:
            return date(value, 1, 1)
        except:
            return None
    return None

def fix_dates():
    with app.app_context():
        connection = db.engine.connect()
        result = connection.execute(text("SELECT * FROM parcalar"))  # ✅
        rows = result.fetchall()

        print(f"\n🔧 {len(rows)} kayıt inceleniyor...\n")

        for row in rows:
            parca_id = row[0]
            sbt_raw = row[11]
            bsb_raw = row[14]
            created_raw = row[10]

            sbt = convert_to_date_safe(sbt_raw)
            bsb = convert_to_date_safe(bsb_raw)
            created = convert_to_date_safe(created_raw)

            db.session.execute(
                text("""
                    UPDATE parcalar SET 
                        son_bakim_tarihi = :sbt, 
                        bir_sonraki_bakim = :bsb, 
                        created_at = :created 
                    WHERE id = :id
                """),
                {"sbt": sbt, "bsb": bsb, "created": created, "id": parca_id}
            )
            print(f"✅ Güncellendi: ID={parca_id}")

        db.session.commit()
        print("\n🎉 Tüm hatalı tarihler düzeltildi.")

if __name__ == "__main__":
    fix_dates()
