# contact-qr

A small Python tool I built to make networking easier: it turns my contact details into a QR code. When someone scans it with their phone camera, they get an "Add Contact" prompt with my name, title, phone, email, website, LinkedIn, and photo already filled in. No app, website, or internet connection needed.

## How it works

1. My details live in `private/contact.json`, which is gitignored and never leaves my computer.
2. `make_qr.py` builds a **vCard** (the standard contact-card format phones use) from those details.
3. It encodes the vCard into a QR code and saves a PNG (to keep on my phone) and an SVG (for sharp printing).

It makes two versions:

| File | What's inside | Trade-off |
|---|---|---|
| `contact-qr.png` | All details, no photo | Small, simple code that scans instantly |
| `contact-qr-photo.png` | All details plus a tiny photo | Much denser code; needs a steadier scan |

## Decisions

- **Everything stored inside the QR code (static), not a link to a hosted file.**
  *Why:* it works offline, costs nothing, and my phone number never has to sit on a public web page. The trade-off is that changing my details means generating a new code.
- **Private details are kept out of the code and the repo.** The script reads a gitignored JSON file, and the generated images (which contain the details) are gitignored too. `contact.example.json` shows the format with placeholder values.
  *Why:* the repo can be public without exposing any personal information.
- **LinkedIn is added twice:** as an iPhone "social profile" and as a labeled second URL.
  *Why:* some Android contact apps ignore social profiles, so the URL is a fallback.
- **The photo is shrunk automatically** to the largest square JPEG that fits a ~1.4 KB budget, without dropping below quality 40.
  *Why:* a QR code holds about 3 KB at most, and a bigger photo would make the code too dense to scan from a phone screen.
- **Error correction:** medium for the no-photo version (still scans if part of the code is smudged) and low for the photo version (leaves the most room for data).

## Run it

```bash
cp contact.example.json private/contact.json   # first time only, then fill in your details
./run.sh
```

`run.sh` sets up a Python virtual environment on the first run, installs the dependencies, generates the codes into `output/`, and opens that folder.

**Built with:** Python, [segno](https://github.com/heuer/segno) (QR codes), [Pillow](https://python-pillow.org/) (photo resizing).

## License

All rights reserved. See [LICENSE](LICENSE).
