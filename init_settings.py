from app import create_app, db
from app.models import Settings

app = create_app()

with app.app_context():
    if not Settings.query.first():
        s = Settings(site_name='PORT Liman Yönetimi')
        db.session.add(s)
        db.session.commit()
        print('✅ Settings satırı başarıyla eklendi.')
    else:
        print('✅ Zaten bir Settings satırı mevcut.')
