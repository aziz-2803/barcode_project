from app import create_app, db
from app.models import User, Settings

app = create_app()

with app.app_context():
    # إنشاء مستخدم أدمن
    admin = User(username="admin", password="1234", role="Admin")
    db.session.add(admin)

    # إنشاء إعدادات افتراضية للموقع
    site_settings = Settings(site_name="PORT Liman Yönetimi")
    db.session.add(site_settings)

    db.session.commit()

print("✅ Admin ve Site Ayarları başarıyla oluşturuldu.")
