"""Build a contact card (vCard) and turn it into a scannable QR code.

Reads private/contact.json (gitignored) and writes to output/ (gitignored):
  contact-qr.png / .svg              contact card without a photo (most reliable to scan)
  contact-qr-photo.png / .svg        same card with a small embedded photo (denser code)
  contact-qr.vcf / contact-qr-photo.vcf   the raw contact cards, handy for testing
"""

import base64
import io
import json
import sys
from pathlib import Path

import segno
from PIL import Image

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "private" / "contact.json"
OUTPUT = ROOT / "output"

# A QR code holds at most ~2,950 bytes. Keep the photo well under that so the
# code stays scannable from a phone screen.
PHOTO_BUDGET_BYTES = 1400


def escape(value):
    """Escape characters that have special meaning in vCard values."""
    return (value.replace("\\", "\\\\").replace(",", "\\,")
                 .replace(";", "\\;").replace("\n", "\\n"))


def small_photo(path, crop):
    """Return the largest square JPEG thumbnail that fits PHOTO_BUDGET_BYTES, base64-encoded."""
    image = Image.open(path).convert("RGB")
    if crop:
        image = image.crop(tuple(crop))
    for size in (96, 80, 72, 64, 56, 48, 40):
        thumb = image.resize((size, size), Image.LANCZOS)
        # Below quality 40 the face gets blocky, so shrink the size instead
        for quality in (60, 50, 40):
            buffer = io.BytesIO()
            thumb.save(buffer, "JPEG", quality=quality, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            if len(encoded) <= PHOTO_BUDGET_BYTES:
                return encoded, size, quality
    sys.exit("Photo could not be shrunk enough to fit in a QR code.")


def build_vcard(info, photo=None):
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape(info['last_name'])};{escape(info['first_name'])};;;",
        f"FN:{escape(info['first_name'])} {escape(info['last_name'])}",
        f"NICKNAME:{escape(info['nickname'])}",
        f"TITLE:{escape(info['title'])}",
        f"TEL;TYPE=CELL:{info['phone']}",
        f"EMAIL;TYPE=INTERNET:{info['email']}",
        f"URL:{info['website']}",
        # iPhone shows this as a LinkedIn social profile
        f"X-SOCIALPROFILE;TYPE=linkedin:{info['linkedin']}",
        # Backup for phones without a social profile field: a second, labeled URL
        f"item1.URL:{info['linkedin']}",
        "item1.X-ABLabel:LinkedIn",
    ]
    if photo:
        lines.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{photo}")
    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def save(vcard, name, error):
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / f"{name}.vcf").write_text(vcard, encoding="utf-8")
    qr = segno.make(vcard, error=error, micro=False, encoding="utf-8")
    # Scale so the PNG is roughly 1,200 px wide: sharp on a phone, fine for printing
    scale = max(4, 1200 // (qr.symbol_size()[0]))
    qr.save(OUTPUT / f"{name}.png", scale=scale, border=4)
    qr.save(OUTPUT / f"{name}.svg", scale=10, border=4)
    print(f"  {name}.png  QR version {qr.version} ({qr.symbol_size()[0]} squares wide), "
          f"{len(vcard.encode('utf-8'))} bytes")


def main():
    if not CONFIG.exists():
        sys.exit("Missing private/contact.json. Copy contact.example.json there and fill it in.")
    info = json.loads(CONFIG.read_text(encoding="utf-8"))

    print("Saved to output/:")
    # Medium error correction: still scans if a bit of the code is smudged or covered
    save(build_vcard(info), "contact-qr", error="m")

    photo_path = ROOT / info["photo"] if info.get("photo") else None
    if photo_path and photo_path.exists():
        photo, size, quality = small_photo(photo_path, info.get("photo_crop"))
        # Low error correction leaves the most room for the photo
        save(build_vcard(info, photo), "contact-qr-photo", error="l")
        print(f"  (photo shrunk to {size}x{size} px, JPEG quality {quality})")


if __name__ == "__main__":
    main()
