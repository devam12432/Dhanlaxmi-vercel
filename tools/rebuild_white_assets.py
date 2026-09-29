from pathlib import Path
from PIL import Image
import colorsys

root = Path(__file__).resolve().parent.parent / 'frontend' / 'public' / 'assets'

def pure_white_background(src_name, out_name):
    im = Image.open(root / src_name).convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # The supplied marks are deep blue; replace low-saturation paper,
            # shadows, and cream photo background with exact white.
            if s < 0.42 or v < 0.28:
                if s < 0.42 or v < 0.28:
                    px[x, y] = (255, 255, 255, 255)
            else:
                px[x, y] = (r, g, b, 255)
    im.convert('RGB').save(root / out_name, optimize=True)

pure_white_background('angel-one-logo-clean.png', 'angel-one-logo-pdf.png')
pure_white_background('angel-one-stamp-clean.png', 'angel-one-stamp-pdf.png')
print('rebuilt pure-white logo and stamp assets')
