# contact-qr

A small Python tool I built to make networking easier: it turns my contact details into a QR code. When someone scans it with their phone camera, they get an "Add Contact" prompt with my name, title, phone, email, website, and LinkedIn already filled in. No app, website, or internet connection needed.

## How it works

1. My details live in `private/contact.json`, which is gitignored and never leaves my computer.
2. `make_qr.py` builds a **vCard** (the standard contact-card format phones use) from those details.
3. It encodes the vCard into a QR code and saves a PNG (to keep on my phone) and an SVG (for sharp printing).

## Decisions

- **Everything stored inside the QR code (static), not a link to a hosted file.**
  *Why:* it works offline, costs nothing, and my phone number never has to sit on a public web page. The trade-off is that changing my details means generating a new code.
- **Private details are kept out of the code and the repo.** The script reads a gitignored JSON file, and the generated files (which contain the details) are gitignored too. `contact.example.json` shows the format with placeholder values.
  *Why:* the repo can be public without exposing any personal information.
- **No contact photo.** I tested a version with a small embedded photo.
  *Why:* a QR code holds about 3 KB at most. Even a heavily shrunk photo nearly quintupled the data, making the code far denser and the photo too low-quality to be worth it.
- **LinkedIn goes in the phone's social profile field** rather than as an extra URL.
  *Why:* it shows up labeled as LinkedIn in the contact card without duplicating the link.
- **Medium error correction.**
  *Why:* the code still scans if part of it is smudged or covered, while staying simple enough to scan quickly from a phone screen.

## Run it

```bash
cp contact.example.json private/contact.json   # first time only, then fill in your details
./run.sh
```

`run.sh` sets up a Python virtual environment on the first run, installs the dependency, generates the code into `output/`, and opens that folder.

**Built with:** Python and [segno](https://github.com/heuer/segno) for QR code generation.

## License

All rights reserved. See [LICENSE](LICENSE).
