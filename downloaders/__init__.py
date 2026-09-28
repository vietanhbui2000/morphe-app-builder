#!/usr/bin/env python3
"""
Registry and dispatcher for modular downloaders.
"""

from typing import List, Tuple
from core.models import AppConfig
from downloaders.base import BaseDownloader
from downloaders.apkmirror import APKMirrorDownloader
from downloaders.apkpure import APKPureDownloader
from downloaders.ia import IADownloader
from downloaders.direct import DirectDownloader

DOWNLOADERS = {
    "apkmirror": APKMirrorDownloader(),
    "apkpure": APKPureDownloader(),
    "ia": IADownloader(),
    "direct": DirectDownloader(),
}

def get_download_sources_for_app(app: AppConfig) -> List[Tuple[str, BaseDownloader, str]]:
    """Return ordered list of (display_name, downloader_instance, source_url) configured for this app."""
    sources: List[Tuple[str, BaseDownloader, str]] = []

    if app.apkmirror_url:
        dl = DOWNLOADERS["apkmirror"]
        sources.append((dl.display_name, dl, app.apkmirror_url))
    if app.apkpure_url:
        dl = DOWNLOADERS["apkpure"]
        sources.append((dl.display_name, dl, app.apkpure_url))
    if app.ia_url:
        dl = DOWNLOADERS["ia"]
        sources.append((dl.display_name, dl, app.ia_url))
    if app.direct_url:
        dl = DOWNLOADERS["direct"]
        sources.append((dl.display_name, dl, app.direct_url))

    return sources
