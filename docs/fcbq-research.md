# Investigació FCBQ (basquetcatala.cat)

Data: 2026-11-07. Resultat: **fonts en viu NO verificades i accés automatitzat bloquejat per la FCBQ per a agents d'IA.** Per això l'aplicació funciona només en mode DEMO.

## Què s'ha comprovat (3 peticions, una sola vegada, UA identificat)
| Prova | Resultat |
|---|---|
| `GET /robots.txt` | 200. `Allow` només per a `/apps/web/continguts/`, `/apps/web/vistes/`, `/apps/web/templates/`. Bloc explícit **`Disallow: /` per a agents d'IA** (ClaudeBot, Claude-User, GPTBot, ChatGPT-User, PerplexityBot, CCBot, etc.). |
| `GET /` | **403 Forbidden** (HTML de 8,7 KB que carrega reCAPTCHA). |

Conclusió: l'accés automatitzat des d'aquest entorn (agent d'IA) contravé el robots.txt i topa amb una protecció anti-bot. Per la regla del brief («no saltar autenticació ni proteccions»), **no s'han fet més peticions**: no s'han provat `/competicions/resultats/pdf/...`, `/estadistiques/...` ni cap endpoint JSON. Res d'això està verificat.

## Les 4 preguntes del brief
1. **Endpoint JSON/API legítim:** no verificat. No s'ha inspeccionat què carrega la web (el 403 ho impedeix sense esquivar-lo). No s'han revisat els termes d'ús. Camí legítim: demanar accés/dades obertes a la FCBQ.
2. **Latència de les estadístiques «en viu»:** no verificat. Només cal mesurar-ho amb permís, en un partit real.
3. **Cerca de club i llistat de grups/partits:** no verificat. El brief suggereix jornada 0 per grup, però no hi ha índex club→grups conegut sense recórrer el lloc.
4. **Parcials per període o acumulats:** no verificat. L'esquema manté `parcialsTipus: desconegut` fins que es comprovi; la UI no suposa res.

## Què fer a continuació (ordre)
1. Escriure a la FCBQ (suport/Acta Digital) demanant: permís d'ús, feed o API oficial, i condicions per a dades de menors. Esmentar l'ús previst (consulta familiar, baix volum, amb caché).
2. Si concedeixen accés, implementar un `Source` nou (vegeu `basquet-live/app/sources.py`) i verificar les 4 preguntes amb dades reals abans de fiar-se'n.
3. Mentrestant, mantenir el mode DEMO etiquetat. Alternativa sense scraping: l'app oficial «Bàsquet Català».

## Regles aplicades al codi
- Cap peticions a la FCBQ al codi ni als tests.
- Tot el que falta es mostra «—», mai 0.
- Origen (`font`) i hora d'actualització sempre visibles; avís si és antic.
- Fixtures etiquetades `DEMO`; noms de jugadors fictius (res de menors reals).
