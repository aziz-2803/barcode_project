import os
import barcode
from barcode.writer import ImageWriter

# تطهير الأحرف غير المدعومة (مثل Ö → O، Ü → U)
def temizle_karakterler(text):
    replacements = {
        'Ö': 'O',
        'Ü': 'U',
        'Ç': 'C',
        'Ş': 'S',
        'Ğ': 'G',
        'İ': 'I',
        'ö': 'o',
        'ü': 'u',
        'ç': 'c',
        'ş': 's',
        'ğ': 'g',
        'ı': 'i',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# تأكد أن المجلد موجود
os.makedirs("barcodes", exist_ok=True)

# القائمة الأصلية
barcodes = [
    "KAVRAMA-001",
    "KAVRAMA-002",
    "POLIP-001",
    "POLIP-002",
    "ÖRÜMCEK-001"  # فيها مشكلة
]

# توليد الصور
for code in barcodes:
    temiz_kod = temizle_karakterler(code)
    barcode_class = barcode.get_barcode_class('code128')
    my_code = barcode_class(temiz_kod, writer=ImageWriter())
    my_code.save(os.path.join("barcodes", temiz_kod))

print("Barkodlar başarıyla oluşturuldu.")
