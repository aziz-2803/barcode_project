from app import create_app, db
from app.models import Item
from datetime import datetime

app = create_app()

with app.app_context():
    items = [
        Item(name='Vinç A1', location='Depo Alanı', maintenance_date=datetime(2025, 3, 10).date(), status='Çalışıyor'),
        Item(name='Forklift B2', location='Yükleme Alanı', maintenance_date=datetime(2025, 5, 12).date(), status='Bakım Gerekli'),
        Item(name='Pompa C3', location='Atölye', maintenance_date=datetime(2025, 4, 8).date(), status='Arızalı'),
        Item(name='Konveyör E5', location='Üretim Hattı', maintenance_date=datetime(2025, 6, 1).date(), status='Bakım Gerekli'),
        Item(name='Kompresör F6', location='Bakım Alanı', maintenance_date=datetime(2025, 2, 20).date(), status='Çalışıyor'),
        Item(name='Kazan G7', location='Enerji Merkezi', maintenance_date=datetime(2025, 1, 15).date(), status='Arızalı'),
        Item(name='Vinç H8', location='Depo', maintenance_date=datetime(2025, 3, 20).date(), status='Bakım Gerekli'),
        Item(name='Forklift I9', location='Yükleme Bölgesi', maintenance_date=datetime(2025, 7, 18).date(), status='Çalışıyor'),
        Item(name='Pompa J10', location='Saha Alanı', maintenance_date=datetime(2025, 9, 10).date(), status='Bakım Gerekli')
    ]
    
    db.session.bulk_save_objects(items)
    db.session.commit()
    print("Örnek ekipmanlar başarıyla eklendi ✅")
