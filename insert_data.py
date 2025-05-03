from app import create_app
from app.models import db, Parca
from datetime import date

app = create_app()

with app.app_context():
    parcalar = [
        Parca(
            barcode="KAVRAMA-001",
            model_adi="SENNEBOGEN-835",
            ekipman_turu="Kavrama",
            konum="6.bölge",
            durum="Arızalı",
            son_bakim_tarihi=date(2025, 1, 15),
            bir_sonraki_bakim=None,
            bakim_periyodu="6 ay",
            kisa_aciklama="Sol çene yavaş kapanıyordu, piston iç sızdırma vardı.",
            yuk_kapasitesi="3m3",
            sorumlu_kisi="Erdal Kesici"
        ),
        Parca(
            barcode="KAVRAMA-002",
            model_adi="SENNEBOGEN-835",
            ekipman_turu="Kavrama",
            konum="6.bölge",
            durum="Arızalı",
            son_bakim_tarihi=date(2025, 1, 16),
            bir_sonraki_bakim=None,
            bakim_periyodu="6 ay",
            kisa_aciklama="Hidrolik hortumlar aşınmıştı, 2 tanesi yenilendi.",
            yuk_kapasitesi="3m3",
            sorumlu_kisi="Erdal Kesici"
        ),
        Parca(
            barcode="POLIP-001",
            model_adi="SENNEBOGEN-835",
            ekipman_turu="Polip",
            konum="7.bölge",
            durum="Kullanıma hazır",
            son_bakim_tarihi=date(2025, 1, 18),
            bir_sonraki_bakim=None,
            bakim_periyodu="1 yıl",
            kisa_aciklama="3 numaralı çene tam kapanmıyor, hidromotor çıkartıldı.",
            yuk_kapasitesi="1.5m3",
            sorumlu_kisi="Erdal Kesici"
        ),
        Parca(
            barcode="POLIP-002",
            model_adi="SENNEBOGEN-835",
            ekipman_turu="Polip",
            konum="7.bölge",
            durum="Kullanıma hazır",
            son_bakim_tarihi=date(2025, 1, 19),
            bir_sonraki_bakim=None,
            bakim_periyodu="1 yıl",
            kisa_aciklama="Hortum uçlarında çatlama görüldü, 4 hortum değiştirildi.",
            yuk_kapasitesi="1.5m3",
            sorumlu_kisi="Erdal Kesici"
        ),
        Parca(
            barcode="ORUMCEK-001",
            model_adi="SENNEBOGEN-870",
            ekipman_turu="Örümcek",
            konum="6.bölge",
            durum="Arızalı",
            son_bakim_tarihi=date(2025, 1, 24),
            bir_sonraki_bakim=None,
            bakim_periyodu="1 yıl",
            kisa_aciklama="Bom kızak raylarında aşırı kirlenme vardı, komple temizlendi.",
            yuk_kapasitesi="2m3",
            sorumlu_kisi="Harun Akan"
        ),
    ]

    db.session.add_all(parcalar)
    db.session.commit()
    print("Parçalar başarıyla veritabanına eklendi.")
