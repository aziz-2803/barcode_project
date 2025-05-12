from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    if not User.query.filter_by(username="admin").first():
        hashed_password = generate_password_hash("admin123")
        admin = User(username="admin", password=hashed_password, role="Admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcı başarıyla oluşturuldu: kullanıcı adı = admin, şifre = admin123")
    else:
        print("Admin zaten mevcut.")
