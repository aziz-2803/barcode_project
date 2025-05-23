from flask import Blueprint, jsonify
from app.models import Parca
from datetime import datetime

api = Blueprint('api', __name__)

# ========= GET: جلب بيانات قطعة =========
@api.route('/api/parca/<int:parca_id>', methods=['GET'])
def get_parca(parca_id):
    parca = Parca.query.get(parca_id)
    if not parca:
        return jsonify({'error': 'Parça bulunamadı'}), 404

    return jsonify({
        'id': parca.id,
        'barcode': parca.barcode,
        'ekipman_turu': parca.ekipman_turu,
        'model_adi': parca.model_adi,
        'konum': parca.konum,
        'durum': parca.durum,
        'bir_sonraki_bakim': _to_date_str(parca.bir_sonraki_bakim),
        'son_bakim_tarihi': _to_date_str(parca.son_bakim_tarihi),
        'created_at': _to_date_str(parca.created_at),
        'bakim_dongusu': parca.bakim_dongusu,
        'bakim_durumu': parca.bakim_durum,
        'kisa_aciklama': parca.kisa_aciklama,
        'yuk_kapasitesi': parca.yuk_kapasitesi,
        'sorumlu_kisi': parca.sorumlu_kisi,
        'notlar': parca.notlar
    })

# ====== البحث باستخدام barcode (لـ Flutter) ======
@api.route('/api/barcode/<string:barcode>', methods=['GET'])
def get_parca_by_barcode(barcode):
    parca = Parca.query.filter_by(barcode=barcode).first()
    if not parca:
        return jsonify({'error': 'Parça bulunamadı'}), 404

    return jsonify({
        'id': parca.id,
        'barcode': parca.barcode,
        'ekipman_turu': parca.ekipman_turu,
        'model_adi': parca.model_adi,
        'konum': parca.konum,
        'durum': parca.durum,
        'bir_sonraki_bakim': _to_date_str(parca.bir_sonraki_bakim),
        'son_bakim_tarihi': _to_date_str(parca.son_bakim_tarihi),
        'created_at': _to_date_str(parca.created_at),
        'bakim_dongusu': parca.bakim_dongusu,
        'notlar': parca.notlar
    })
    
# ========= دالة آمنة لتحويل التواريخ =========
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
