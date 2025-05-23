import os
from app import db, create_app
from app.models import Parca
import barcode
from barcode.writer import ImageWriter

# 1. إنشاء التطبيق وتفعيل السياق
app = create_app()

with app.app_context():
    # 2. إنشاء مجلد لحفظ الباركودات
    os.makedirs("generated_barcodes", exist_ok=True)

    # 3. استرجاع جميع القطع
    parcalar = Parca.query.all()

    for parca in parcalar:
        value = parca.barcode
        if not value:
            continue

        file_path = os.path.join("generated_barcodes", f"{value}.png")

        # 4. توليد الباركود وحفظه
        code128 = barcode.get("code128", value, writer=ImageWriter())
        code128.save(file_path)

        print(f"✅ Barkod oluşturuldu: {file_path}")
