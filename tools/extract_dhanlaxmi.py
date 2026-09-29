from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
src = Image.open('/home/ubuntu/upload/Screenshot2026-09-23153934.png').convert('RGB')
out = root / 'frontend' / 'public' / 'assets'
# Crops are taken from the supplied reference only: logo at top-left and
# the circular Dhanlaxmi stamp at the lower-left of the invoice.
logo = src.crop((24, 0, 224, 55))
stamp = src.crop((38, 548, 122, 627))
logo.save(out / 'dhanlaxmi-logo-pdf.png', optimize=True)
stamp.save(out / 'dhanlaxmi-stamp-pdf.png', optimize=True)
# The browser preview uses the same clean white-backed assets.
logo.save(out / 'dhanlaxmi-logo-clean.png', optimize=True)
stamp.save(out / 'dhanlaxmi-stamp-clean.png', optimize=True)
print('dhanlaxmi assets extracted')
