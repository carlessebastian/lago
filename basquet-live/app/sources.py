"""Fonts de dades. Només existeix DemoSource: no hi ha cap font FCBQ verificada
ni autoritzada (vegeu docs/fcbq-research.md). Un Source nou ha d'implementar:
  search_clubs(q) -> [str]; list_matches(club) -> [raw]; get_match(id) -> raw | None
"""
import json
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "demo.json"


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


class DemoSource:
    nom = "DEMO"

    def __init__(self, path=FIXTURE, now=None):
        self._data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._now = now or datetime.now(timezone.utc)

    def _raw(self, m):
        m = dict(m)
        base = self._now.replace(hour=0, minute=0, second=0, microsecond=0)
        h, mi = map(int, m.pop("hora").split(":"))
        m["dataPartit"] = (base + timedelta(days=m.pop("diesDesDeAvui"), hours=h, minutes=mi)).isoformat()
        m["font"] = "DEMO (dades fictícies)"
        m["actualitzatA"] = (self._now - timedelta(seconds=m.pop("fa_segons", 30))).isoformat()
        return m

    def search_clubs(self, q):
        q = fold(q)
        clubs = {n for m in self._data["partits"] for n in (m["local"], m["visitant"])}
        return sorted(c for c in clubs if q and q in fold(c))

    def list_matches(self, club):
        c = fold(club)
        return [self._raw(m) for m in self._data["partits"]
                if c in fold(m["local"]) or c in fold(m["visitant"])]

    def get_match(self, mid):
        for m in self._data["partits"]:
            if str(m["id"]) == str(mid):
                return self._raw(m)
        return None
