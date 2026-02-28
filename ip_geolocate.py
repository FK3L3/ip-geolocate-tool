#!/usr/bin/env python3
"""
Batch IP geolocation lookup tool.

Usage examples:
  python3 ip_geolocate.py --ips 8.8.8.8 1.1.1.1
  python3 ip_geolocate.py --input ips.txt --output results.csv
"""

from __future__ import annotations

import argparse
import csv
import ipaddress
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://ipwho.is/{ip}"


@dataclass
class GeoResult:
    ip: str
    success: bool
    country: str = ""
    region: str = ""
    city: str = ""
    latitude: str = ""
    longitude: str = ""
    isp: str = ""
    org: str = ""
    asn: str = ""
    error: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a list of IPs and return location details for each."
    )
    parser.add_argument(
        "--ips",
        nargs="*",
        default=[],
        help="IP addresses provided directly in the command.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a file containing one IP per line.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional CSV output path.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=8.0,
        help="HTTP timeout per request in seconds (default: 8).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between requests in seconds (default: 0).",
    )
    parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="Preserve duplicate IPs instead of deduplicating before lookup.",
    )
    return parser.parse_args()


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value.strip())
        return True
    except ValueError:
        return False


def load_ips(
    cli_ips: list[str], input_file: Path | None, keep_duplicates: bool = False
) -> list[str]:
    ips: list[str] = []
    ips.extend(ip.strip() for ip in cli_ips if ip.strip())

    if input_file:
        for line in input_file.read_text(encoding="utf-8").splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            ips.append(candidate)
    elif not sys.stdin.isatty():
        for line in sys.stdin.read().splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            ips.append(candidate)

    if keep_duplicates:
        return ips

    unique_ips: list[str] = []
    seen = set()
    for ip in ips:
        if ip not in seen:
            seen.add(ip)
            unique_ips.append(ip)
    return unique_ips


def fetch_geo(ip: str, timeout: float) -> GeoResult:
    req = Request(API_URL.format(ip=ip), headers={"User-Agent": "ip-geolocate/1.0"})
    try:
        with urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return GeoResult(ip=ip, success=False, error=f"HTTP {exc.code}")
    except URLError as exc:
        return GeoResult(ip=ip, success=False, error=f"Network error: {exc.reason}")
    except Exception as exc:  # noqa: BLE001
        return GeoResult(ip=ip, success=False, error=f"Unexpected error: {exc}")

    if not payload.get("success", False):
        return GeoResult(
            ip=ip,
            success=False,
            error=str(payload.get("message", "API returned failure")),
        )

    connection = payload.get("connection") or {}
    return GeoResult(
        ip=ip,
        success=True,
        country=str(payload.get("country", "")),
        region=str(payload.get("region", "")),
        city=str(payload.get("city", "")),
        latitude=str(payload.get("latitude", "")),
        longitude=str(payload.get("longitude", "")),
        isp=str(connection.get("isp", "")),
        org=str(connection.get("org", "")),
        asn=str(connection.get("asn", "")),
    )


def print_table(results: Iterable[GeoResult]) -> None:
    headers = ["IP", "Status", "Country", "Region", "City", "Lat", "Lon", "ISP", "ASN"]
    rows = []
    for row in results:
        rows.append(
            [
                row.ip,
                "OK" if row.success else f"ERR: {row.error}",
                row.country,
                row.region,
                row.city,
                row.latitude,
                row.longitude,
                row.isp,
                row.asn,
            ]
        )

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def format_row(cells: list[str]) -> str:
        return " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(cells))

    print(format_row(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(format_row(row))


def write_csv(results: Iterable[GeoResult], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "ip",
                "success",
                "country",
                "region",
                "city",
                "latitude",
                "longitude",
                "isp",
                "org",
                "asn",
                "error",
            ]
        )
        for row in results:
            writer.writerow(
                [
                    row.ip,
                    row.success,
                    row.country,
                    row.region,
                    row.city,
                    row.latitude,
                    row.longitude,
                    row.isp,
                    row.org,
                    row.asn,
                    row.error,
                ]
            )


def main() -> int:
    args = parse_args()
    ips = load_ips(args.ips, args.input, keep_duplicates=args.keep_duplicates)
    if not ips:
        print("No IPs provided. Use --ips and/or --input.", file=sys.stderr)
        return 2

    invalid = [ip for ip in ips if not is_valid_ip(ip)]
    if invalid:
        print("Invalid IP(s): " + ", ".join(invalid), file=sys.stderr)
        return 2

    results: list[GeoResult] = []
    for idx, ip in enumerate(ips):
        results.append(fetch_geo(ip, args.timeout))
        if args.delay > 0 and idx < len(ips) - 1:
            time.sleep(args.delay)

    print_table(results)
    if args.output:
        write_csv(results, args.output)
        print(f"\nSaved CSV: {args.output}")

    failed = [r for r in results if not r.success]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
