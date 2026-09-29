#!/usr/bin/env python3
"""
QR Tracker - Static Site Generator

Reads config.json and generates:
  1. Redirect HTML pages in docs/r/<slug>/index.html  (for GitHub Pages)
  2. QR code PNG images in qr-images/<slug>.png
  3. A CNAME file for custom domain setup
  4. An index.html that tracks direct visits and redirects

Usage:
    pip install -r requirements.txt
    python generate.py
"""

import json
import os
import shutil
import sys
from pathlib import Path

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
except ImportError:
    qrcode = None


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
TEMPLATE_PATH = ROOT / "templates" / "redirect.html"
DOCS_DIR = ROOT / "docs"
QR_DIR = ROOT / "qr-images"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_config() -> dict:
    """Load and validate config.json."""
    if not CONFIG_PATH.exists():
        print(f"ERROR: {CONFIG_PATH} not found.")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ["domain", "ga_measurement_id", "codes"]
    for key in required:
        if key not in cfg:
            print(f"ERROR: Missing required config key: '{key}'")
            sys.exit(1)
    return cfg


def load_template() -> str:
    """Load the redirect HTML template."""
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: {TEMPLATE_PATH} not found.")
        sys.exit(1)
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def render_template(template: str, variables: dict) -> str:
    """Replace {{KEY}} placeholders in the template with values."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def generate_redirect_page(template: str, cfg: dict, code: dict) -> None:
    """Generate a single redirect page for a campaign."""
    slug = code["slug"]
    dest = code["destination"]

    out_dir = DOCS_DIR / "r" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    html = render_template(template, {
        "GA_ID": cfg["ga_measurement_id"],
        "SLUG": slug,
        "DESTINATION": dest,
        "DELAY_MS": cfg.get("redirect_delay_ms", 400),
    })

    out_file = out_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"  [OK] docs/r/{slug}/index.html -> {dest}")


def generate_qr_image(domain: str, code: dict) -> None:
    """Generate a QR code PNG image for a campaign."""
    if qrcode is None:
        return  # skip silently if library not installed

    slug = code["slug"]
    url = f"https://{domain}/r/{slug}"

    QR_DIR.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_path = QR_DIR / f"{slug}.png"
    img.save(str(img_path))
    print(f"  [OK] qr-images/{slug}.png  ({url})")


def generate_index_page(cfg: dict) -> None:
    """Generate an index.html that tracks direct visits and redirects."""
    domain = cfg["domain"]
    ga_id = cfg["ga_measurement_id"]
    destination = cfg.get("default_redirect", f"https://{domain}")
    delay_ms = cfg.get("redirect_delay_ms", 400)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Redirecting...</title>

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga_id}');
    gtag('event', 'direct_visit', {{
      campaign: 'homepage',
      destination: '{destination}'
    }});
  </script>

  <!-- Fallback redirect for no-JS clients -->
  <meta http-equiv="refresh" content="2;url={destination}">

  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: #f8f9fa;
      color: #333;
    }}
    .card {{
      text-align: center;
      padding: 2rem;
    }}
    .spinner {{
      width: 32px;
      height: 32px;
      border: 3px solid #e0e0e0;
      border-top: 3px solid #333;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 1rem;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    a {{ color: #0066cc; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="spinner"></div>
    <p>Redirecting...</p>
    <p><small><a href="{destination}">Click here</a> if not redirected automatically.</small></p>
  </div>

  <script>
    setTimeout(function() {{
      window.location.href = '{destination}';
    }}, {delay_ms});
  </script>
</body>
</html>"""

    index_path = DOCS_DIR / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"  [OK] docs/index.html (direct visit redirect)")


def generate_cname(domain: str) -> None:
    """Generate a CNAME file for GitHub Pages custom domain."""
    cname_path = DOCS_DIR / "CNAME"
    cname_path.write_text(domain, encoding="utf-8")
    print(f"  [OK] docs/CNAME ({domain})")


def generate_404_page(cfg: dict) -> None:
    """Generate a custom 404 page that redirects to default."""
    default = cfg.get("default_redirect", f"https://{cfg['domain']}")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Not Found</title>
  <meta http-equiv="refresh" content="3;url={default}">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex; justify-content: center; align-items: center;
      min-height: 100vh; margin: 0; background: #f8f9fa; color: #333;
      text-align: center;
    }}
    a {{ color: #0066cc; }}
  </style>
</head>
<body>
  <div>
    <h1>404</h1>
    <p>This QR code is not active.</p>
    <p><a href="{default}">Go to {cfg['domain']}</a></p>
  </div>
</body>
</html>"""
    path = DOCS_DIR / "404.html"
    path.write_text(html, encoding="utf-8")
    print(f"  [OK] docs/404.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("QR Tracker - Static Site Generator\n")

    cfg = load_config()
    template = load_template()
    domain = cfg["domain"]
    codes = cfg["codes"]

    print(f"Domain:  {domain}")
    print(f"GA4 ID:  {cfg['ga_measurement_id']}")
    print(f"Codes:   {len(codes)}\n")

    # Clean output directories
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate all pages
    print("Generating redirect pages:")
    for code in codes:
        generate_redirect_page(template, cfg, code)

    # Generate QR code images
    if qrcode is not None:
        print("\nGenerating QR code images:")
        for code in codes:
            generate_qr_image(domain, code)
    else:
        print("\nSkipping QR image generation (install 'qrcode[pil]' to enable)")

    # Generate supporting files
    print("\nGenerating supporting files:")
    generate_index_page(cfg)
    generate_cname(domain)
    generate_404_page(cfg)

    print(f"\nDone! {len(codes)} campaign(s) generated.")


if __name__ == "__main__":
    main()
