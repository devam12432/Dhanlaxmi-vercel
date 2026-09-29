from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'frontend' / 'public' / 'assets'

def remove_light_bg(im, threshold=245):
    rgba = im.convert('RGBA')
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (255, 255, 255, 0)
    return rgba

# Crop the actual mark from the supplied photographed logo reference.
logo = Image.open(ASSETS / 'angel-one-logo.webp').convert('RGB')
logo = logo.crop((250, 530, 1325, 1060))
logo = remove_light_bg(logo, 238)
logo.save(ASSETS / 'angel-one-logo-clean.png', optimize=True)

# Crop the stamp artwork away from the surrounding canvas and remove its light background.
stamp = Image.open(ASSETS / 'angel-one-stamp.webp').convert('RGB')
stamp = stamp.crop((390, 40, 1660, 1410))
stamp = remove_light_bg(stamp, 238)
stamp.save(ASSETS / 'angel-one-stamp-clean.png', optimize=True)

# Remove the white background around the supplied signature.
sign = Image.open(ASSETS / 'authorized-signature.png')
sign = remove_light_bg(sign, 242)
sign.save(ASSETS / 'authorized-signature-clean.png', optimize=True)

print('clean assets generated')
