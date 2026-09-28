#!/usr/bin/env python3
"""
APKPure Downloader: scrapes APKPure version pages and downloads APK / XAPK.
Supports BeautifulSoup if installed, with regex fallback.
"""

import re
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from core.http import http_client
from core.logger import log_info, log_warn
from downloaders.base import BaseDownloader

class APKPureDownloader(BaseDownloader):
    @property
    def name(self) -> str:
        return "apkpure"

    @property
    def display_name(self) -> str:
        return "APKPure"

    def get_versions(self, url: str) -> list[str]:
        clean_url = url.rstrip("/")
        if not clean_url.endswith("/versions"):
            versions_url = f"{clean_url}/versions"
        else:
            versions_url = clean_url

        html = http_client.get_html(versions_url)
        if not html:
            return []

        versions = []
        for v in re.findall(r'data-dt-version="([^"]+)"', html):
            if v not in versions:
                versions.append(v)

        return versions

    def download(
        self,
        url: str,
        version: str,
        arch: str,
        dpi: str,
        output_path: Path,
        app_id: str = ""
    ) -> Optional[Path]:
        clean_url = url.rstrip("/")
        if clean_url.endswith("/versions") or clean_url.endswith("/download"):
            clean_url = clean_url.rsplit("/", 1)[0]

        dl_page_url = f"{clean_url}/download/{version}" if version else f"{clean_url}/download"
        log_info(f"[APKPure] Fetching download page {dl_page_url}...", indent=2)

        html = http_client.get_html(dl_page_url)
        if not html:
            return None

        # Missing versions render an error page (or the latest version) with status 200, so check the title
        title_m = re.search(r"<title>([^<]*)</title>", html, re.IGNORECASE)
        title = title_m.group(1) if title_m else ""
        if version and version not in title:
            log_warn(f"[APKPure] Version {version} page not found (got \"{title.strip()[:80]}\")", indent=2)
            return None

        dl_url = None
        if HAS_BS4:
            soup = BeautifulSoup(html, "html.parser")
            dl_btn = soup.select_one("a#download_link")
            if dl_btn and dl_btn.get("href"):
                dl_url = dl_btn["href"]

        if not dl_url:
            match = re.search(r'href="(https://d\.apkpure\.com/b/(?:XAPK|APK)/[^"]+)"', html)
            dl_url = match.group(1).replace("&amp;", "&") if match else None

        if not dl_url or "d.apkpure.com/b/" not in dl_url:
            log_warn("[APKPure] Could not resolve download link", indent=2)
            return None

        ext = ".xapk" if "/b/XAPK/" in dl_url else ".apk"
        dest_path = output_path.parent / f"{output_path.name}{ext}"

        log_info(f"[APKPure] Downloading payload to {dest_path.name}...", indent=2)
        if http_client.download_file(dl_url, dest_path, referer=dl_page_url):
            return dest_path

        return None
