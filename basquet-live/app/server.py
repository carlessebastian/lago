"""Servei mínim (només stdlib). Ús: python -m app.server [port]  (des de basquet-live/)."""
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .schema import is_stale, normalize_match
from .sources import DemoSource

STATIC = Path(__file__).resolve().parent.parent / "static"


def api(source, path, qs, now=None):
    """Retorna (status, objecte JSON). Separat del HTTP per poder-lo provar."""
    now = now or datetime.now(timezone.utc)
    if path == "/api/clubs":
        return 200, {"font": source.nom, "clubs": source.search_clubs(qs.get("q", [""])[0])}
    if path == "/api/partits":
        club = qs.get("club", [""])[0]
        filtre = qs.get("filtre", ["tots"])[0]
        ms = [normalize_match(r) for r in source.list_matches(club)]
        if filtre == "avui":
            ms = [m for m in ms if m["dataPartit"] and m["dataPartit"][:10] == now.astimezone().date().isoformat()
                  or m["estat"] == "en_joc"]
        elif filtre == "pendents":
            ms = [m for m in ms if m["estat"] in ("programat", "en_joc")]
        ms.sort(key=lambda m: m["dataPartit"] or "")
        for m in ms:
            m["antic"] = is_stale(m, now)
        for m in ms:
            m.pop("jugadors"), m.pop("periodes")
        return 200, {"partits": ms}
    if path.startswith("/api/partit/"):
        raw = source.get_match(path.rsplit("/", 1)[1])
        if raw is None:
            return 404, {"error": "partit no trobat"}
        m = normalize_match(raw)
        m["antic"] = is_stale(m, now)
        return 200, m
    return 404, {"error": "no trobat"}


def make_handler(source):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            u = urlparse(self.path)
            if u.path in ("/", "/index.html"):
                body, ctype, status = (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8", 200
            else:
                status, obj = api(source, u.path, parse_qs(u.query))
                body, ctype = json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8"
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass
    return H


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Mode DEMO a http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), make_handler(DemoSource())).serve_forever()
