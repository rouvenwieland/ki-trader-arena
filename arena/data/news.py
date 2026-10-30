"""Nachrichten & Stimmung aus öffentlichen Quellen: RSS, GDELT, Reddit (RSS/JSON). Alles mit Ausfalltoleranz."""
from __future__ import annotations

import re
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import quote

from arena.data.http import HttpFehler, get

RSS = {
    "BBC Welt": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Wirtschaft": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "Guardian Welt": "https://www.theguardian.com/world/rss",
    "Guardian Wirtschaft": "https://www.theguardian.com/business/rss",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "NPR Politik": "https://feeds.npr.org/1014/rss.xml",
    "Tagesschau": "https://www.tagesschau.de/index~rss2.xml",
}
REDDIT = ["Bitcoin", "CryptoCurrency", "wallstreetbets", "politics", "worldnews", "Polymarket"]
STOP = set("the a an of to in on for and or is are will be by with at as from that this who what when how "
           "der die das und oder ist sind wird im in am zu von mit für auf the before after over under".split())


def _zeit(s: str | None) -> float:
    try:
        return parsedate_to_datetime(s).timestamp()
    except (TypeError, ValueError):
        return 0.0


def rss(name: str, url: str) -> list[dict]:
    try:
        txt = get(url, text=True, ttl=300)
        wurzel = ET.fromstring(txt)
    except (HttpFehler, ET.ParseError):
        return []
    out = []
    for it in wurzel.iter("item"):
        out.append({"quelle": name, "titel": (it.findtext("title") or "").strip(), "url": (it.findtext("link") or "").strip(),
                    "zeit": _zeit(it.findtext("pubDate")), "text": re.sub("<[^>]+>", "", it.findtext("description") or "")[:300]})
    return out


def reddit(sub: str, n: int = 15) -> list[dict]:
    try:
        d = get(f"https://www.reddit.com/r/{sub}/hot.json", {"limit": n}, ttl=300)
        return [{"quelle": f"r/{sub}", "titel": c["data"]["title"], "url": "https://reddit.com" + c["data"]["permalink"],
                 "zeit": c["data"]["created_utc"], "text": (c["data"].get("selftext") or "")[:200],
                 "punkte": c["data"]["score"]} for c in d["data"]["children"]]
    except (HttpFehler, KeyError, TypeError):
        pass
    try:  # RSS-Variante, wird seltener geblockt
        txt = get(f"https://www.reddit.com/r/{sub}/.rss", text=True, ttl=300)
        w = ET.fromstring(txt)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        return [{"quelle": f"r/{sub}", "titel": e.findtext("a:title", "", ns), "url": e.find("a:link", ns).get("href", ""),
                 "zeit": time.time(), "text": ""} for e in w.findall("a:entry", ns)[:n]]
    except (HttpFehler, ET.ParseError, AttributeError):
        return []


def gdelt(suche: str, n: int = 10) -> list[dict]:
    try:
        d = get("https://api.gdeltproject.org/api/v2/doc/doc",
                {"query": suche, "mode": "artlist", "format": "json", "maxrecords": n, "sort": "datedesc"}, ttl=600, versuche=1)
        return [{"quelle": "GDELT:" + a.get("domain", ""), "titel": a["title"], "url": a["url"], "zeit": time.time(), "text": ""}
                for a in d.get("articles", [])]
    except (HttpFehler, KeyError, ValueError):
        return []


def alle_nachrichten(max_alter_h: float = 36) -> list[dict]:
    out = []
    for n, u in RSS.items():
        out += rss(n, u)
    for s in REDDIT[:3]:
        out += reddit(s)
    grenze = time.time() - max_alter_h * 3600
    out = [x for x in out if x["zeit"] == 0 or x["zeit"] >= grenze]
    out.sort(key=lambda x: -x["zeit"])
    return out


def stichworte(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-zäöüß0-9]{4,}", text.lower()) if w not in STOP}


def passende(nachrichten: list[dict], stichwort_mengen: dict[str, set[str]], min_treffer: int = 2) -> dict[str, list[dict]]:
    """Ordnet Nachrichten Positionen zu: ≥ min_treffer gemeinsame Stichworte (oder ein Eigenname wie Ticker)."""
    out: dict[str, list[dict]] = {}
    for key, kw in stichwort_mengen.items():
        for n in nachrichten:
            gem = kw & stichworte(n["titel"] + " " + n.get("text", ""))
            if len(gem) >= min_treffer or (len(kw) <= 2 and gem):
                out.setdefault(key, []).append(n)
    return out


def suche(frage: str, nachrichten: list[dict], n: int = 8) -> list[dict]:
    kw = stichworte(frage)
    bewertet = sorted(((len(kw & stichworte(x["titel"] + " " + x.get("text", ""))), x) for x in nachrichten),
                      key=lambda t: (-t[0], -t[1]["zeit"]))
    return [x for s, x in bewertet if s > 0][:n]
