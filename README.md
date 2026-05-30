# IP Geolocation Tool

Script: `ip_geolocate.py`

## Tools Used

- `Python 3` runtime (CLI script execution)
- Python standard library modules:
  `argparse`, `csv`, `ipaddress`, `json`, `sys`, `time`,
  `dataclasses`, `pathlib`, `typing`, `urllib.request`, `urllib.error`
- External geolocation API: `https://ipwho.is/{ip}`
- Command-line usage examples use standard shell tools like `cat` for stdin piping

## Quick start

```bash
python3 ip_geolocate.py --ips 8.8.8.8 1.1.1.1
```

## Scan from file

Create a text file with one IP per line:

```text
8.8.8.8
1.1.1.1
208.67.222.222
```

Run:

```bash
python3 ip_geolocate.py --input ips.txt
```

Or paste from stdin:

```bash
cat ips.txt | python3 ip_geolocate.py
```

## Export to CSV

```bash
python3 ip_geolocate.py --input ips.txt --output results.csv
```

## Optional controls

- `--timeout 12`: request timeout per IP
- `--delay 0.5`: delay between requests (useful for rate limits)
- `--keep-duplicates`: keeps repeated IPs (default behavior deduplicates before lookup)

## Web UI (use on any phone — no server needed)

The easiest way to use this on your phone is via **GitHub Pages** — a free
hosted URL that works from any browser, anywhere.

### Enable GitHub Pages (one-time setup)

1. Go to your repo on GitHub → **Settings** → **Pages**
2. Under *Build and deployment*, set **Source** to `Deploy from a branch`
3. Set **Branch** to `main` and **folder** to `/docs`
4. Click **Save**

GitHub will publish the app at:

```
https://fk3l3.github.io/ip-geolocate-tool/
```

Bookmark that URL on your phone. Done — no installs, no server, works anywhere.

### How it works

`docs/index.html` is a fully self-contained page that calls the
[ipwho.is](https://ipwho.is) geolocation API directly from your browser.
No Python or Flask required.

### Features

- Enter one or more IPs (one per line) and tap **Locate IPs**
- Tap **My IP** to auto-detect and look up your current public IP
- Results stream in as cards with country flag, city, ISP, and ASN
- Interactive map (Leaflet / OpenStreetMap) pins all located IPs
- Dark / light theme toggle, persisted across sessions
- Works as a local file too — just open `docs/index.html` in any browser

---

## Self-hosted Web UI (optional, requires Python)

If you want to run the web UI on your own server:

```bash
pip install flask
python3 app.py
```

Open `http://localhost:5000` in your browser, or on your phone via:

```
http://<your-machine-ip>:5000
```
