from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # تحقق إن كان المستخدم موجود مسبقًا
    existing = User.query.filter_by(username='admin').first()
    if not existing:
        admin = User(
            username='admin',
            password=generate_password_hash('123456'),  # كلمة مرور مشفرة
            role='Admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcısı başarıyla oluşturuldu.")
    else:
        print("Admin kullanıcısı zaten mevcut.")
