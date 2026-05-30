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

## Web UI (mobile-friendly)

A browser-based interface lets you look up IPs from any device — including your phone.

### Install

```bash
pip install flask
```

### Run

```bash
python3 app.py
```

Open `http://localhost:5000` in your browser.

### Use on your phone

Start the server on your computer, then find your machine's local IP address:

```bash
# macOS / Linux
hostname -I   # or: ifconfig | grep 'inet '
```

On your phone (same Wi-Fi network), open:

```
http://<your-machine-ip>:5000
```

### Features

- Enter one or more IPs (one per line) and tap **Locate IPs**
- Tap **My IP** to auto-detect and look up your current public IP
- Results displayed as cards with country flag, city, ISP, and ASN
- Interactive map (Leaflet/OpenStreetMap) shows all located IPs
- Dark / light theme toggle, persisted across sessions
