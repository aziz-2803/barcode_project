from flask import Blueprint, jsonify, request
from app.models import Parca
from app import db
from datetime import datetime
from dateutil.relativedelta import relativedelta

api = Blueprint('api', __name__)

# ========= GET: جلب بيانات قطعة =========
@api.route('/api/parca/<int:parca_id>', methods=['GET'])
def get_parca(parca_id):
    parca = Parca.query.get(parca_id)
    if not parca:
        return jsonify({'error': 'Parça bulunamadı'}), 404

    bir_sonraki_bakim = parca.bir_sonraki_bakim
    if not bir_sonraki_bakim and parca.son_bakim_tarihi and parca.bakim_dongusu:
        try:
            ay_sayisi = int(parca.bakim_dongusu.strip())
            bir_sonraki_bakim = parca.son_bakim_tarihi + relativedelta(months=ay_sayisi)
        except:
            bir_sonraki_bakim = None

    return jsonify({
        'id': parca.id,
        'barcode': parca.barcode,
        'ekipman_turu': parca.ekipman_turu,
        'model_adi': parca.model_adi,
        'konum': parca.konum,
        'durum': parca.durum,
        'bir_sonraki_bakim': _to_date_str(bir_sonraki_bakim),
        'son_bakim_tarihi': _to_date_str(parca.son_bakim_tarihi),
        'created_at': _to_date_str(parca.created_at),
        'bakim_dongusu': parca.bakim_dongusu,
        'bakim_durumu': parca.bakim_durum,
        'kisa_aciklama': parca.kisa_aciklama,
        'yuk_kapasitesi': parca.yuk_kapasitesi,
        'sorumlu_kisi': parca.sorumlu_kisi
    })

# ====== GET: جلب البيانات باستخدام باركود (لتطبيق Flutter) ======
@api.route('/api/barcode/<string:barcode>', methods=['GET'])
def get_parca_by_barcode(barcode):
    parca = Parca.query.filter_by(barcode=barcode).first()
    if not parca:
        return jsonify({'error': 'Parça bulunamadı'}), 404

    bir_sonraki_bakim = parca.bir_sonraki_bakim
    if not bir_sonraki_bakim and parca.son_bakim_tarihi and parca.bakim_dongusu:
        try:
            ay_sayisi = int(parca.bakim_dongusu.strip())
            bir_sonraki_bakim = parca.son_bakim_tarihi + relativedelta(months=ay_sayisi)
        except:
            bir_sonraki_bakim = None

    return jsonify({
        'id': parca.id,
        'barcode': parca.barcode,
        'ekipman_turu': parca.ekipman_turu,
        'model_adi': parca.model_adi,
        'konum': parca.konum,
        'durum': parca.durum,
        'bir_sonraki_bakim': _to_date_str(bir_sonraki_bakim),
        'son_bakim_tarihi': _to_date_str(parca.son_bakim_tarihi),
        'created_at': _to_date_str(parca.created_at),
        'bakim_dongusu': parca.bakim_dongusu,
        'sorumlu_kisi': parca.sorumlu_kisi,
        'kisa_aciklama': parca.kisa_aciklama
    })

# ====== PUT: تعديل قطعة باستخدام الباركود من تطبيق Flutter ======
@api.route('/api/barcode/<string:barcode>', methods=['PUT'])
def update_parca_by_barcode(barcode):
    parca = Parca.query.filter_by(barcode=barcode).first()
    if not parca:
        return jsonify({'error': 'Parça bulunamadı'}), 404

    data = request.get_json()

    parca.durum = data.get('durum', parca.durum)
    parca.konum = data.get('konum', parca.konum)
    parca.sorumlu_kisi = data.get('sorumlu_kisi', parca.sorumlu_kisi)
    parca.kisa_aciklama = data.get('kisa_aciklama', parca.kisa_aciklama)

    # تاريخ آخر صيانة
    son_bakim_str = data.get('son_bakim_tarihi')
    if son_bakim_str:
        try:
            parca.son_bakim_tarihi = datetime.fromisoformat(son_bakim_str)
        except:
            pass

    db.session.commit()
    return jsonify({'message': 'Parça başarıyla güncellendi'})

# ========= دالة آمنة لتحويل التواريخ إلى نص =========
def _to_date_str(value):
    try:
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, str):
            return value
        elif value is None:
            return None
        else:
            return str(value)
    except Exception:
        return None
