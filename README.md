# QR Tracker

A free, self-hosted QR code tracking system using **GitHub Pages** + **Google Analytics**.

QR codes point to your domain → a static redirect page fires a GA4 event → user is forwarded to the final destination. You get full scan analytics in Google Analytics for free.

## How It Works

```
┌──────────┐  scan   ┌─────────────────────────┐  redirect   ┌──────────────┐
│  QR Code │ ──────► │  yourdomain.com/r/slug   │ ──────────► │  Final Site  │
│ (printed)│         │  (GitHub Pages)          │             │              │
└──────────┘         │  📊 GA4 event fires      │             └──────────────┘
                     └─────────────────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.8+
- A GitHub account
- A Google Analytics 4 property ([create one here](https://analytics.google.com))
- A custom domain (optional but recommended)

### 2. Install & Generate

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/qr-tracker.git
cd qr-tracker

# Install dependencies
pip install -r requirements.txt

# Edit config.json with your GA4 ID and campaigns
# (see Configuration below)

# Generate the site + QR images
python generate.py
```

### 3. Push to GitHub & Enable Pages

```bash
git add .
git commit -m "Generate QR tracker site"
git push
```

Then in your GitHub repo:
1. Go to **Settings → Pages**
2. Set **Source** to `Deploy from a branch`
3. Set **Branch** to `main` and **Folder** to `/docs`
4. Click **Save**

Your site will be live at `https://YOUR_USERNAME.github.io/qr-tracker/` within a few minutes.

### 4. Custom Domain (Recommended)

To use your own domain (e.g., `qr.yourdomain.com`):

1. In your DNS provider, add a **CNAME record**:
   - **Name:** `qr` (or `@` for root domain)
   - **Value:** `YOUR_USERNAME.github.io`

2. In GitHub repo **Settings → Pages → Custom domain**, enter your domain

3. Check **Enforce HTTPS**

4. Update `domain` in `config.json` and regenerate

GitHub provides free SSL for custom domains automatically.

## Configuration

Edit `config.json`:

```json
{
  "domain": "qr.yourdomain.com",
  "ga_measurement_id": "G-XXXXXXXXXX",
  "redirect_delay_ms": 400,
  "default_redirect": "https://yourdomain.com",
  "codes": [
    {
      "slug": "spring-sale",
      "destination": "https://mystore.com/spring-sale",
      "label": "Spring Sale 2027 Flyer"
    },
    {
      "slug": "menu",
      "destination": "https://myrestaurant.com/menu",
      "label": "Restaurant Menu"
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `domain` | Your custom domain (or `username.github.io/qr-tracker`) |
| `ga_measurement_id` | Your GA4 Measurement ID (starts with `G-`) |
| `redirect_delay_ms` | Milliseconds to wait before redirecting (lets GA event fire) |
| `default_redirect` | Where the 404 page sends unknown URLs |
| `codes` | Array of QR code campaigns |
| `codes[].slug` | URL path segment (e.g., `menu` → `yourdomain.com/r/menu`) |
| `codes[].destination` | The final URL users are sent to |
| `codes[].label` | Human-readable name (shown on the index page) |

## Adding a New QR Code

1. Add an entry to the `codes` array in `config.json`
2. Run `python generate.py`
3. Commit and push
4. Print the QR image from `qr-images/`

## Viewing Analytics

All scan data flows into your Google Analytics property:

1. Go to [analytics.google.com](https://analytics.google.com)
2. Navigate to **Reports → Engagement → Events**
3. Look for the `qr_scan` event
4. You can see breakdowns by:
   - **Campaign** (which QR code was scanned)
   - **Geography** (where users scanned from)
   - **Device** (mobile vs desktop, OS, browser)
   - **Time** (when scans occurred)

### Setting Up a Custom GA4 Report (Optional)

For a dedicated QR dashboard:
1. Go to **Explore → Blank**
2. Add dimensions: `campaign`, `city`, `device category`
3. Add metrics: `event count`, `total users`
4. Filter to event name = `qr_scan`

## Project Structure

```
qr-tracker/
├── config.json              ← Your campaigns & settings
├── generate.py              ← Generates everything
├── requirements.txt         ← Python dependencies
├── templates/
│   └── redirect.html        ← Redirect page template
├── docs/                    ← Generated site (GitHub Pages serves this)
│   ├── index.html           ← Campaign listing page
│   ├── 404.html             ← Custom 404 page
│   ├── CNAME                ← Custom domain config
│   └── r/
│       ├── campaign1/
│       │   └── index.html   ← Redirect + GA4 tracking
│       └── campaign2/
│           └── index.html
└── qr-images/               ← Generated QR code PNGs (for printing)
    ├── campaign1.png
    └── campaign2.png
```

## Updating a Destination URL

This is the key advantage over static QR codes: **you can change where a QR code points without reprinting it.**

1. Edit the `destination` in `config.json`
2. Run `python generate.py`
3. Commit and push

The printed QR code still points to `yourdomain.com/r/slug` — but now that page redirects somewhere new.

## License

MIT
