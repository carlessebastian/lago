import unittest
from datetime import datetime, timezone

from app.schema import is_stale, normalize_match, normalize_player
from app.server import api
from app.sources import DemoSource

NOW = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)  # fixture DEMO


class SchemaTests(unittest.TestCase):
    def test_missing_is_none_never_zero(self):
        m = normalize_match({"id": 1})
        self.assertIsNone(m["puntsLocal"])
        self.assertEqual(m["estat"], "desconegut")
        self.assertEqual(m["parcialsTipus"], "desconegut")
        p = normalize_player({"nom": "X"})
        self.assertTrue(all(p[k] is None for k in ("pts", "t2", "t3", "tl", "faltes", "min")))

    def test_real_zero_kept_and_bad_shots_dropped(self):
        p = normalize_player({"pts": 0, "t2": "0/3", "t3": "5/2", "tl": "x"})
        self.assertEqual(p["pts"], 0)
        self.assertEqual(p["t2"], "0/3")
        self.assertIsNone(p["t3"])
        self.assertIsNone(p["tl"])

    def test_stale(self):
        base = {"id": 1, "estat": "en_joc", "actualitzatA": NOW.isoformat()}
        self.assertFalse(is_stale(normalize_match(base), NOW))
        self.assertTrue(is_stale(normalize_match({**base, "actualitzatA": "2026-11-07T11:50:00+00:00"}), NOW))
        self.assertTrue(is_stale(normalize_match({"id": 1}), NOW))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.src = DemoSource(now=NOW)

    def test_search_accent_insensitive(self):
        _, r = api(self.src, "/api/clubs", {"q": ["qbasket"]}, NOW)
        self.assertIn("QBASKET SANT CUGAT", r["clubs"])
        self.assertEqual(api(self.src, "/api/clubs", {"q": [""]}, NOW)[1]["clubs"], [])

    def test_pendents_filter(self):
        _, r = api(self.src, "/api/partits", {"club": ["qbasket"], "filtre": ["pendents"]}, NOW)
        self.assertEqual({m["estat"] for m in r["partits"]}, {"en_joc", "programat"})

    def test_labelled_demo_and_stale_flag(self):
        _, r = api(self.src, "/api/partits", {"club": ["qbasket"], "filtre": ["tots"]}, NOW)
        self.assertTrue(all("DEMO" in m["font"] for m in r["partits"]))
        by = {m["id"]: m for m in r["partits"]}
        self.assertFalse(by["demo-1"]["antic"])
        self.assertTrue(by["demo-3"]["antic"])

    def test_match_detail_nulls(self):
        s, m = api(self.src, "/api/partit/demo-1", {}, NOW)
        self.assertEqual(s, 200)
        self.assertIsNone(m["jugadors"]["local"][1]["t2"])
        self.assertEqual(api(self.src, "/api/partit/nope", {}, NOW)[0], 404)


if __name__ == "__main__":
    unittest.main()
