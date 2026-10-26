"""Build a contact card (vCard) and turn it into a scannable QR code.

Reads private/contact.json (gitignored) and writes to output/ (gitignored):
  contact-qr.png   QR code to save on a phone (~1,200 px)
  contact-qr.svg   same QR code for sharp printing at any size
  contact-qr.vcf   the raw contact card, handy for testing
"""

import json
import sys
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "private" / "contact.json"
OUTPUT = ROOT / "output"


def escape(value):
    """Escape characters that have special meaning in vCard values."""
    return (value.replace("\\", "\\\\").replace(",", "\\,")
                 .replace(";", "\\;").replace("\n", "\\n"))


def build_vcard(info):
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
        # Shows in the phone's social profile section as LinkedIn
        f"X-SOCIALPROFILE;TYPE=linkedin:{info['linkedin']}",
        "END:VCARD",
    ]
    return "\r\n".join(lines) + "\r\n"


def main():
    if not CONFIG.exists():
        sys.exit("Missing private/contact.json. Copy contact.example.json there and fill it in.")
    info = json.loads(CONFIG.read_text(encoding="utf-8"))
    vcard = build_vcard(info)

    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "contact-qr.vcf").write_text(vcard, encoding="utf-8")
    # Medium error correction: still scans if a bit of the code is smudged or covered
    qr = segno.make(vcard, error="m", micro=False, encoding="utf-8")
    # Scale so the PNG is roughly 1,200 px wide: sharp on a phone, fine for printing
    scale = max(4, 1200 // qr.symbol_size()[0])
    qr.save(OUTPUT / "contact-qr.png", scale=scale, border=4)
    qr.save(OUTPUT / "contact-qr.svg", scale=10, border=4)
    print(f"Saved contact-qr.png, .svg and .vcf to output/ "
          f"(QR version {qr.version}, {len(vcard.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
