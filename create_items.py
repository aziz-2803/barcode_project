from app import create_app
from app.models import db, Parca
from datetime import datetime

app = create_app()

with app.app_context():
    parcalar = [
        Parca(
            barcode='POLIP-001',
            ekipman_turu='Polip',
            model_adi='SENNEBOGEN-835',
            konum='6.bölge',
            durum='Kullanıma hazır',
            bir_sonraki_bakim=datetime(2025, 6, 15).date(),
            kisa_aciklama='Yeni teslim alınan ekipman.',
            yuk_kapasitesi='3m3',
            sorumlu_kisi='Erdal Kesici'
        ),
        Parca(
            barcode='POLIP-002',
            ekipman_turu='Polip',
            model_adi='SENNEBOGEN-830',
            konum='4.bölge',
            durum='Bakım Gerekli',
            bir_sonraki_bakim=datetime(2025, 5, 20).date(),
            kisa_aciklama='Hidrolik hortumda kaçak var.',
            yuk_kapasitesi='2.5m3',
            sorumlu_kisi='Ahmet Demir'
        ),
        Parca(
            barcode='ORUMCEK-001',
            ekipman_turu='Örümcek',
            model_adi='CAT-320',
            konum='3.bölge',
            durum='Kullanıma hazır',
            bir_sonraki_bakim=datetime(2025, 7, 10).date(),
            kisa_aciklama='Tam kapasiteyle çalışıyor.',
            yuk_kapasitesi='2m3',
            sorumlu_kisi='Mehmet Yıldız'
        ),
        Parca(
            barcode='KAVRAMA-001',
            ekipman_turu='Kavrama',
            model_adi='HITACHI-ZX200',
            konum='1.bölge',
            durum='Arızalı',
            bir_sonraki_bakim=datetime(2025, 8, 5).date(),
            kisa_aciklama='Motor arızası var.',
            yuk_kapasitesi='1.8m3',
            sorumlu_kisi='Fatma Kara'
        ),
        Parca(
            barcode='KAVRAMA-002',
            ekipman_turu='Kavrama',
            model_adi='HITACHI-ZX220',
            konum='2.bölge',
            durum='Kullanıma hazır',
            bir_sonraki_bakim=datetime(2025, 9, 12).date(),
            kisa_aciklama='Son bakım tamamlandı.',
            yuk_kapasitesi='2m3',
            sorumlu_kisi='Ali Koç'
        ),
    ]

    db.session.bulk_save_objects(parcalar)
    db.session.commit()
    print("Tüm parçalar başarıyla eklendi.")
