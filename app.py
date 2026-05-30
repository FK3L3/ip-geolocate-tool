from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

import requests as _req
from flask import Flask, jsonify, render_template, request

from ip_geolocate import fetch_geo, is_valid_ip

app = Flask(__name__)

_MAX_IPS = 50
_TIMEOUT = 8.0


def _process(ip: str) -> dict:
    if not is_valid_ip(ip):
        return {"ip": ip, "success": False, "error": "Invalid IP address",
                "country": "", "country_code": "", "region": "", "city": "",
                "latitude": "", "longitude": "", "isp": "", "org": "", "asn": ""}
    return asdict(fetch_geo(ip, _TIMEOUT))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/myip")
def myip():
    ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "")
        or request.remote_addr
        or ""
    )
    return jsonify({"ip": ip})


@app.post("/api/lookup")
def lookup():
    data = request.get_json(silent=True) or {}
    raw: list = data.get("ips", [])

    if not raw:
        return jsonify({"error": "No IPs provided"}), 400

    ips = list(dict.fromkeys(s.strip() for s in raw if isinstance(s, str) and s.strip()))
    if len(ips) > _MAX_IPS:
        return jsonify({"error": f"Maximum {_MAX_IPS} IPs per request"}), 400

    with ThreadPoolExecutor(max_workers=min(len(ips), 10)) as pool:
        results = list(pool.map(_process, ips))

    return jsonify({"results": results})


@app.get("/api/abuse")
def abuse_proxy():
    ip = request.args.get("ip", "").strip()
    key = request.headers.get("X-Abuse-Key", "").strip()
    if not is_valid_ip(ip):
        return jsonify({"error": "Invalid IP address"}), 400
    if not key:
        return jsonify({"error": "No API key provided"}), 400
    try:
        r = _req.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": key, "Accept": "application/json"},
            timeout=8,
        )
        return jsonify(r.json()), r.status_code
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
