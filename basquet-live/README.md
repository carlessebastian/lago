# Bàsquet Live (mode DEMO)

Cerca de club → partits (pendents/avui/tots) → detall amb marcador, parcials i estadístiques. Interfície en català; el que falta es mostra «—».

**Només hi ha dades DEMO fictícies.** No hi ha cap font FCBQ verificada ni autoritzada: vegeu `../docs/fcbq-research.md`.

    cd basquet-live
    python -m app.server 8000      # UI a http://127.0.0.1:8000
    python -m unittest discover -s tests

Per afegir una font real, implementeu el contracte de `app/sources.py` (`search_clubs`, `list_matches`, `get_match`) un cop la FCBQ ho autoritzi.
