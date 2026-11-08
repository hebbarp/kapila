# -*- coding: utf-8 -*-
"""
Sources (ಮೂಲಗಳು) — the first mashable data sources.

    news     ಸುದ್ದಿ     ( topic -- list )   headlines: ಶೀರ್ಷಿಕೆ ಮೂಲ ಕೊಂಡಿ ಸಮಯ
    weather  ಹವಾಮಾನ   ( place -- rec )    ಸ್ಥಳ ತಾಪಮಾನ ಮಳೆ ಗಾಳಿ ಸ್ಥಿತಿ ಅಕ್ಷಾಂಶ ರೇಖಾಂಶ ಸಮಯ
    wiki     ವಿಕಿ      ( title -- rec )    ಶೀರ್ಷಿಕೆ ಸಾರಾಂಶ ಕೊಂಡಿ ಚಿತ್ರ [ಅಕ್ಷಾಂಶ ರೇಖಾಂಶ]

Kannada input goes to Kannada providers; anything else goes to English ones.

Safety (docs/mashables.md §12):
  * only the fixed hosts in ALLOWED_HOSTS can be fetched; there is no general fetch
  * at most FETCHES_PER_RUN source calls per program run (vm.fetch_budget)
  * responses are cached for CACHE_TTL seconds
  * uncached upstream requests are rate-limited per client (vm.client_id)
"""

import html
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from email.utils import parsedate_to_datetime

USER_AGENT = "Kapila/0.1 (+https://kapila.matsyaai.com)"
TIMEOUT = 8                 # seconds per upstream request
MAX_BYTES = 6 * 1024 * 1024
CACHE_TTL = 600             # seconds
FETCHES_PER_RUN = 5         # source calls per program run
CLIENT_LIMIT = 60           # uncached upstream requests per client per hour
MAX_ITEMS = 20              # records returned by news

ALLOWED_HOSTS = {
    "news.google.com",
    "www.prajavani.net",
    "kannada.oneindia.com",
    "tv9kannada.com",
    "www.kannadaprabha.com",
    "geocoding-api.open-meteo.com",
    "api.open-meteo.com",
    "nominatim.openstreetmap.org",
    "kn.wikipedia.org",
    "en.wikipedia.org",
}

# Kannada publishers' own feeds. Google News's "Kannada edition" serves Hindi
# (checked 2026-11-08), so Kannada topics search these instead.
KANNADA_FEEDS = [
    ("ಪ್ರಜಾವಾಣಿ", "https://www.prajavani.net/stories.rss"),
    ("ಒನ್‌ಇಂಡಿಯಾ ಕನ್ನಡ", "https://kannada.oneindia.com/rss/kannada-news-fb.xml"),
    ("ಟಿವಿ9 ಕನ್ನಡ", "https://tv9kannada.com/feed"),
    ("ಕನ್ನಡಪ್ರಭ", "https://www.kannadaprabha.com/api/v1/collections/latest-news.rss"),
]

# News sections. A topic that names a section reads that section's feeds
# instead of searching headlines. Feeds checked 2026-11-08: each section feed
# was compared with its publisher's main feed, and ones that just repeat the
# main feed (TV9's cinema/state/india) are left out. Prajavani's section feeds
# carry only 1-2 items, so Prajavani is used for headline search only.
TV9, KP, OI = "ಟಿವಿ9 ಕನ್ನಡ", "ಕನ್ನಡಪ್ರಭ", "ಒನ್‌ಇಂಡಿಯಾ ಕನ್ನಡ"
_KP = "https://www.kannadaprabha.com/api/v1/collections/"
SECTIONS = {
    # canonical Kannada name: Kannada aliases, English names, Kannada feeds, Google News (English)
    "ವಾಣಿಜ್ಯ": {
        "kn": ["ವಾಣಿಜ್ಯ", "ಉದ್ಯಮ", "ವ್ಯಾಪಾರ", "ವ್ಯವಹಾರ"], "en": ["business"],
        "feeds": [(TV9, "https://tv9kannada.com/business/feed"), (KP, _KP + "business.rss")],
        "google": "topic:BUSINESS"},
    "ಕ್ರೀಡೆ": {
        "kn": ["ಕ್ರೀಡೆ", "ಕ್ರೀಡಾ"], "en": ["sports", "sport"],
        "feeds": [(TV9, "https://tv9kannada.com/sports/feed"), (KP, _KP + "sports.rss")],
        "google": "topic:SPORTS"},
    "ಸಿನಿಮಾ": {
        "kn": ["ಸಿನಿಮಾ", "ಚಲನಚಿತ್ರ", "ಮನರಂಜನೆ"], "en": ["cinema", "movies", "entertainment"],
        "feeds": [(TV9, "https://tv9kannada.com/entertainment/feed"), (KP, _KP + "cinema.rss"),
                  (OI, "https://kannada.oneindia.com/rss/feeds/kannada-entertainment-fb.xml")],
        "google": "topic:ENTERTAINMENT"},
    "ತಂತ್ರಜ್ಞಾನ": {
        "kn": ["ತಂತ್ರಜ್ಞಾನ", "ಟೆಕ್"], "en": ["technology", "tech"],
        "feeds": [(TV9, "https://tv9kannada.com/technology/feed")],
        "google": "topic:TECHNOLOGY"},
    "ರಾಜಕೀಯ": {
        "kn": ["ರಾಜಕೀಯ"], "en": ["politics"],
        "feeds": [(TV9, "https://tv9kannada.com/politics/feed"), (KP, _KP + "politics.rss")],
        "google": "search:politics"},
    "ರಾಜ್ಯ": {
        "kn": ["ರಾಜ್ಯ", "ಕರ್ನಾಟಕ"], "en": ["karnataka", "state"],
        "feeds": [(TV9, "https://tv9kannada.com/karnataka/feed"), (KP, _KP + "karnataka.rss")],
        "google": "search:Karnataka"},
    "ದೇಶ": {
        "kn": ["ದೇಶ", "ರಾಷ್ಟ್ರೀಯ", "ಭಾರತ"], "en": ["india", "national", "nation"],
        "feeds": [(TV9, "https://tv9kannada.com/national/feed"), (KP, _KP + "nation.rss")],
        "google": "topic:NATION"},
    "ವಿಶ್ವ": {
        "kn": ["ವಿಶ್ವ", "ಜಗತ್ತು", "ಅಂತಾರಾಷ್ಟ್ರೀಯ", "ವಿದೇಶ"], "en": ["world", "international"],
        "feeds": [(TV9, "https://tv9kannada.com/world/feed"), (KP, _KP + "world.rss")],
        "google": "topic:WORLD"},
}
SECTION_BY_NAME = {}
for _key, _sec in SECTIONS.items():
    for _name in _sec["kn"]:
        SECTION_BY_NAME[_name] = (_key, "kn")
    for _name in _sec["en"]:
        SECTION_BY_NAME[_name] = (_key, "en")


# WMO weather codes → Kannada (Open-Meteo uses WMO 4677 codes)
WEATHER_CODES = {
    0: "ನಿರ್ಮಲ ಆಕಾಶ",
    1: "ಬಹುತೇಕ ನಿರ್ಮಲ", 2: "ಭಾಗಶಃ ಮೋಡ", 3: "ಮೋಡ ಕವಿದಿದೆ",
    45: "ಮಂಜು", 48: "ಮಂಜು",
    51: "ತುಂತುರು ಮಳೆ", 53: "ತುಂತುರು ಮಳೆ", 55: "ತುಂತುರು ಮಳೆ",
    56: "ತುಂತುರು ಮಳೆ", 57: "ತುಂತುರು ಮಳೆ",
    61: "ಸಾಧಾರಣ ಮಳೆ", 63: "ಮಳೆ", 65: "ಭಾರೀ ಮಳೆ", 66: "ಮಳೆ", 67: "ಭಾರೀ ಮಳೆ",
    71: "ಹಿಮ", 73: "ಹಿಮ", 75: "ಭಾರೀ ಹಿಮ", 77: "ಹಿಮ",
    80: "ಆಗಾಗ ಮಳೆ", 81: "ಆಗಾಗ ಮಳೆ", 82: "ಭಾರೀ ಮಳೆ",
    85: "ಹಿಮ", 86: "ಹಿಮ",
    95: "ಗುಡುಗು ಸಹಿತ ಮಳೆ", 96: "ಗುಡುಗು ಸಹಿತ ಮಳೆ", 99: "ಗುಡುಗು ಸಹಿತ ಮಳೆ",
}


def _error(msg):
    from .vm import KapilaError  # late import: vm imports this module
    return KapilaError(msg)


def is_kannada(text: str) -> bool:
    return any('ಀ' <= ch <= '೿' for ch in text)


# --- HTTP: allowlist, cache, rate limit --------------------------------------

_cache = {}                  # url → (expires_at, bytes)
_cache_lock = threading.Lock()
_client_hits = {}            # client_id → deque[timestamps]


def _http_get(url: str, client_id=None) -> bytes:
    """Fetch an allowlisted URL, with caching and per-client rate limiting.

    Tests replace this function to avoid the network.
    """
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise _error(f"ಅನುಮತಿ ಇಲ್ಲ / host not allowed: {parts.hostname}")

    now = time.time()
    with _cache_lock:
        hit = _cache.get(url)
        if hit and hit[0] > now:
            return hit[1]
        if client_id is not None:
            q = _client_hits.setdefault(client_id, deque())
            while q and q[0] < now - 3600:
                q.popleft()
            if len(q) >= CLIENT_LIMIT:
                raise _error("ತುಂಬಾ ವಿನಂತಿಗಳು, ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಪ್ರಯತ್ನಿಸಿ / too many requests, try again later")
            q.append(now)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return b""
        raise _error(f"ಮೂಲ ಸಿಗಲಿಲ್ಲ / source failed: {parts.hostname} ({e.code})")
    except Exception as e:
        raise _error(f"ಮೂಲ ಸಿಗಲಿಲ್ಲ / source failed: {parts.hostname} ({e.__class__.__name__})")
    if len(data) > MAX_BYTES:
        raise _error(f"ಉತ್ತರ ತುಂಬಾ ದೊಡ್ಡದು / response too large: {parts.hostname}")

    with _cache_lock:
        _cache[url] = (now + CACHE_TTL, data)
        if len(_cache) > 500:  # drop expired, then oldest
            for k in [k for k, v in _cache.items() if v[0] <= now]:
                _cache.pop(k, None)
            while len(_cache) > 500:
                _cache.pop(next(iter(_cache)))
    return data


def _is_cached(url) -> bool:
    with _cache_lock:
        hit = _cache.get(url)
        return bool(hit and hit[0] > time.time())


def _fetch(vm, url: str) -> bytes:
    """_http_get for a running program: adds the request to the VM's trace."""
    from .trace import add
    parts = urllib.parse.urlsplit(url)
    shown = urllib.parse.unquote(parts.path + ("?" + parts.query if parts.query else ""))
    cached, start = _is_cached(url), time.time()
    try:
        data = _http_get(url, getattr(vm, "client_id", None))
    except Exception as e:
        add(vm, {"k": "fetch", "host": parts.hostname, "path": shown, "cached": False,
                 "ms": int((time.time() - start) * 1000), "error": str(e)})
        raise
    add(vm, {"k": "fetch", "host": parts.hostname, "path": shown, "cached": cached,
             "ms": int((time.time() - start) * 1000), "bytes": len(data)})
    return data


def _get_json(vm, url):
    data = _fetch(vm, url)
    if not data:
        return None
    try:
        return json.loads(data)
    except ValueError:
        raise _error(f"ಮೂಲದ ಉತ್ತರ ಓದಲಾಗಲಿಲ್ಲ / bad response: {urllib.parse.urlsplit(url).hostname}")


def _spend(vm):
    """Charge one source call against the run's budget."""
    left = getattr(vm, "fetch_budget", FETCHES_PER_RUN)
    if left <= 0:
        raise _error(f"ಒಂದು ಓಟದಲ್ಲಿ {FETCHES_PER_RUN} ಮೂಲಗಳು ಮಾತ್ರ / at most {FETCHES_PER_RUN} source calls per run")
    vm.fetch_budget = left - 1


# What each source needs, shown when it is called with nothing on the stack
EXAMPLES = {
    "ಹವಾಮಾನ": '"ಮೈಸೂರು" ಹವಾಮಾನ',
    "ವಿಕಿ": '"ಕುವೆಂಪು" ವಿಕಿ',
}


def _text_arg(vm, what, default=None):
    """The text argument on top of the stack; `default` if the stack is empty."""
    if not vm.stack:
        if default is not None:
            return default
        raise _error(f"{what}: ಯಾವುದರ ಬಗ್ಗೆ? ಉದಾ: {EXAMPLES.get(what, what)}  "
                     f"/ {what} needs text first, e.g. {EXAMPLES.get(what, what)}")
    v = vm.pop()
    if not isinstance(v, str):
        raise _error(f"{what}: ಪಠ್ಯ ಬೇಕು / text expected, got {v!r}")
    return v.strip()


# --- News --------------------------------------------------------------------

def _iso(pub: str) -> str:
    try:
        return parsedate_to_datetime(pub).isoformat()
    except (TypeError, ValueError, IndexError):
        return pub or ""


def _parse_rss(data: bytes, publisher=None):
    """RSS bytes → list of news records. Bad or empty feeds give []."""
    if not data:
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    out = []
    for item in root.iter("item"):
        title = html.unescape((item.findtext("title") or "").strip())
        src = publisher or (item.findtext("source") or "").strip()
        if not publisher and src and title.endswith(" - " + src):
            title = title[: -len(" - " + src)]          # Google News appends " - Publisher"
        if not title:
            continue
        out.append({
            "ಶೀರ್ಷಿಕೆ": title,
            "ಮೂಲ": src,
            "ಕೊಂಡಿ": (item.findtext("link") or "").strip(),
            "ಸಮಯ": _iso((item.findtext("pubDate") or "").strip()),
        })
    return out


def _match_stem(topic: str) -> str:
    """Kannada nouns change their final vowel when inflected (ಬೆಂಗಳೂರು → ಬೆಂಗಳೂರಿನ),
    so match on the topic without its final vowel sign."""
    if len(topic) > 3 and 'ಾ' <= topic[-1] <= 'ೌ':
        return topic[:-1]
    return topic


def _newest_first(records):
    return sorted(records, key=lambda r: r.get("ಸಮಯ", ""), reverse=True)


def builtin_news(vm):
    """( topic -- list ) Headlines about a topic. "" or nothing on the stack = latest.

    A section name (ವಾಣಿಜ್ಯ, ಕ್ರೀಡೆ, ಸಿನಿಮಾ … or business, sports …) reads that
    section's feeds, and each record gets a ವಿಭಾಗ (section) field.
    """
    topic = _text_arg(vm, "ಸುದ್ದಿ", default="")
    _spend(vm)

    section = SECTION_BY_NAME.get(topic) or SECTION_BY_NAME.get(topic.lower())
    if section:
        key, lang = section
        sec = SECTIONS[key]
        items = []
        if lang == "kn":
            for publisher, url in sec["feeds"]:
                try:
                    items.extend(_parse_rss(_fetch(vm, url), publisher))
                except Exception as e:
                    if "too many requests" in str(e):
                        raise
                    continue
        else:
            kind, value = sec["google"].split(":", 1)
            if kind == "topic":
                url = (f"https://news.google.com/rss/headlines/section/topic/{value}"
                       "?hl=en-IN&gl=IN&ceid=IN:en")
            else:
                url = (f"https://news.google.com/rss/search?q={urllib.parse.quote(value)}"
                       "&hl=en-IN&gl=IN&ceid=IN:en")
            items = _parse_rss(_fetch(vm, url))
        for r in items:
            r["ವಿಭಾಗ"] = key
    elif topic == "" or is_kannada(topic):
        items = []
        for publisher, url in KANNADA_FEEDS:
            try:
                items.extend(_parse_rss(_fetch(vm, url), publisher))
            except Exception as e:
                if "too many requests" in str(e):
                    raise
                continue                      # one dead feed shouldn't sink the rest
        if topic:
            stem = _match_stem(topic)
            items = [r for r in items if stem in r["ಶೀರ್ಷಿಕೆ"]]
    else:
        q = urllib.parse.quote(topic)
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        items = _parse_rss(_fetch(vm, url))

    # The same story often appears in several feeds; keep the first of each title.
    seen, unique = set(), []
    for r in _newest_first(items):
        if r["ಶೀರ್ಷಿಕೆ"] not in seen:
            seen.add(r["ಶೀರ್ಷಿಕೆ"])
            unique.append(r)
    vm.push(unique[:MAX_ITEMS])


# --- Weather -----------------------------------------------------------------

def _geocode(vm, place: str):
    """place name → (display name, lat, lon). Open-Meteo first, then OpenStreetMap."""
    q = urllib.parse.quote(place)
    j = _get_json(vm, f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=kn")
    results = (j or {}).get("results") or []
    if results:
        r = results[0]
        return r.get("name") or place, float(r["latitude"]), float(r["longitude"])

    j = _get_json(vm, f"https://nominatim.openstreetmap.org/search?q={q}&format=jsonv2&limit=1&accept-language=kn")
    if j:
        r = j[0]
        name = (r.get("name") or r.get("display_name") or place).split(",")[0]
        return name, float(r["lat"]), float(r["lon"])
    raise _error(f"ಸ್ಥಳ ಸಿಗಲಿಲ್ಲ / place not found: {place}")


def builtin_weather(vm):
    """( place -- rec ) Current weather for a place."""
    place = _text_arg(vm, "ಹವಾಮಾನ")
    if not place:
        raise _error("ಹವಾಮಾನ: ಸ್ಥಳ ಬೇಕು / a place is needed")
    _spend(vm)

    name, lat, lon = _geocode(vm, place)
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat:.4f}&longitude={lon:.4f}"
           "&current=temperature_2m,precipitation,wind_speed_10m,weather_code&timezone=auto")
    cur = ((_get_json(vm, url) or {}).get("current")) or {}
    if not cur:
        raise _error(f"ಹವಾಮಾನ ಸಿಗಲಿಲ್ಲ / no weather for: {place}")
    vm.push({
        "ಸ್ಥಳ": name,
        "ತಾಪಮಾನ": cur.get("temperature_2m"),
        "ಮಳೆ": cur.get("precipitation"),
        "ಗಾಳಿ": cur.get("wind_speed_10m"),
        "ಸ್ಥಿತಿ": WEATHER_CODES.get(cur.get("weather_code"), str(cur.get("weather_code"))),
        "ಅಕ್ಷಾಂಶ": round(lat, 4),
        "ರೇಖಾಂಶ": round(lon, 4),
        "ಸಮಯ": cur.get("time", ""),
    })


# --- Wikipedia ---------------------------------------------------------------

def _wiki_summary(vm, lang, title):
    t = urllib.parse.quote(title.replace(" ", "_"), safe="")
    return _get_json(vm, f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{t}")


def builtin_wiki(vm):
    """( title -- rec ) Wikipedia summary; Kannada titles use kn.wikipedia."""
    title = _text_arg(vm, "ವಿಕಿ")
    if not title:
        raise _error("ವಿಕಿ: ವಿಷಯ ಬೇಕು / a title is needed")
    _spend(vm)
    lang = "kn" if is_kannada(title) else "en"

    j = _wiki_summary(vm, lang, title)
    if not j or j.get("type") == "disambiguation" or not j.get("extract"):
        # Not an exact title: take the best full-text search match instead.
        q = urllib.parse.quote(title)
        s = _get_json(vm, f"https://{lang}.wikipedia.org/w/rest.php/v1/search/page?q={q}&limit=1")
        pages = (s or {}).get("pages") or []
        if pages:
            j = _wiki_summary(vm, lang, pages[0].get("key") or pages[0].get("title", ""))
    if not j or not j.get("extract"):
        raise _error(f"ವಿಕಿಯಲ್ಲಿ ಸಿಗಲಿಲ್ಲ / not found on Wikipedia: {title}")

    rec = {
        "ಶೀರ್ಷಿಕೆ": j.get("title", title),
        "ಸಾರಾಂಶ": j.get("extract", ""),
        "ಕೊಂಡಿ": ((j.get("content_urls") or {}).get("desktop") or {}).get("page", ""),
        "ಚಿತ್ರ": (j.get("thumbnail") or {}).get("source", ""),
    }
    coords = j.get("coordinates")
    if coords:
        rec["ಅಕ್ಷಾಂಶ"] = coords.get("lat")
        rec["ರೇಖಾಂಶ"] = coords.get("lon")
    vm.push(rec)


SOURCE_BUILTINS = {
    'news': builtin_news,
    'weather': builtin_weather,
    'wiki': builtin_wiki,
}
