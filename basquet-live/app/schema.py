"""Normalització a l'esquema Match. Tot el que falta -> None (la UI ho mostra «—»)."""
from datetime import datetime, timezone

ESTATS = {"programat", "en_joc", "finalitzat", "ajornat", "cancellat", "desconegut"}
PARCIALS = {"periode", "acumulat", "desconegut"}
STAT_KEYS = ("dorsal", "nom", "min", "pts", "t2", "t3", "tl", "faltes")


def _int(v):
    if v is None or isinstance(v, bool):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _shot(v):
    """'x/y' vàlid o None."""
    if isinstance(v, str):
        a, _, b = v.partition("/")
        if a.isdigit() and b.isdigit() and int(a) <= int(b):
            return v
    return None


def normalize_player(raw):
    raw = raw or {}
    return {
        "dorsal": raw.get("dorsal") if raw.get("dorsal") not in ("", None) else None,
        "nom": raw.get("nom") or None,
        "min": raw.get("min") if isinstance(raw.get("min"), str) else None,
        "pts": _int(raw.get("pts")),
        "t2": _shot(raw.get("t2")),
        "t3": _shot(raw.get("t3")),
        "tl": _shot(raw.get("tl")),
        "faltes": _int(raw.get("faltes")),
    }


def normalize_match(raw):
    estat = raw.get("estat")
    ptipus = raw.get("parcialsTipus")
    jug = raw.get("jugadors") or {}
    return {
        "id": str(raw["id"]),
        "competicio": raw.get("competicio") or None,
        "local": raw.get("local") or None,
        "visitant": raw.get("visitant") or None,
        "dataPartit": raw.get("dataPartit") or None,
        "estat": estat if estat in ESTATS else "desconegut",
        "puntsLocal": _int(raw.get("puntsLocal")),
        "puntsVisitant": _int(raw.get("puntsVisitant")),
        "periodeActual": _int(raw.get("periodeActual")),
        "rellotge": raw.get("rellotge") or None,
        "parcialsTipus": ptipus if ptipus in PARCIALS else "desconegut",
        "periodes": [
            {"periode": _int(p.get("periode")), "local": _int(p.get("local")),
             "visitant": _int(p.get("visitant"))}
            for p in (raw.get("periodes") or [])
        ],
        "jugadors": {
            "local": [normalize_player(j) for j in jug.get("local") or []],
            "visitant": [normalize_player(j) for j in jug.get("visitant") or []],
        },
        "font": raw.get("font") or "desconeguda",
        "actualitzatA": raw.get("actualitzatA") or None,
    }


def age_seconds(actualitzat_a, now=None):
    if not actualitzat_a:
        return None
    now = now or datetime.now(timezone.utc)
    return (now - datetime.fromisoformat(actualitzat_a)).total_seconds()


def is_stale(match, now=None):
    """Antic: sense hora, >2 min si en joc, >6 h si no."""
    age = age_seconds(match["actualitzatA"], now)
    if age is None:
        return True
    return age > (120 if match["estat"] == "en_joc" else 6 * 3600)
