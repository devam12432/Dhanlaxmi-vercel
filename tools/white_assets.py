from pathlib import Path
from PIL import Image
root = Path(__file__).resolve().parent.parent / 'frontend' / 'public' / 'assets'
for src_name, out_name in [('angel-one-logo-clean.png','angel-one-logo-pdf.png'), ('angel-one-stamp-clean.png','angel-one-stamp-pdf.png')]:
    src = Image.open(root / src_name).convert('RGBA')
    bg = Image.new('RGBA', src.size, 'white')
    bg.alpha_composite(src)
    bg.convert('RGB').save(root / out_name, optimize=True)
print('white PDF assets generated')
