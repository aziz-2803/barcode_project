from app import create_app
from app.models import db, Parca
import barcode
from barcode.writer import ImageWriter
import os

# إنشاء التطبيق
app = create_app()

# تأكد أن مجلد barcodes موجود
barcode_folder = os.path.join(os.path.dirname(__file__), 'barcodes')
os.makedirs(barcode_folder, exist_ok=True)

# داخل السياق
with app.app_context():
    parcalar = Parca.query.all()
    
    for parca in parcalar:
        # توليد رابط الصفحة الخاص بهذه القطعة
        link = f"http://192.168.1.124:5000/detail/{parca.id}"

        # اسم ملف الصورة
        filename = os.path.join(barcode_folder, f"{parca.barcode}.png")

        # توليد الباركود
        code128 = barcode.get('code128', link, writer=ImageWriter())
        code128.save(filename.replace('.png', ''))  # يحذف .png لأن المكتبة تضيفها تلقائيًا

        print(f"Barcod oluşturuldu: {filename}")
