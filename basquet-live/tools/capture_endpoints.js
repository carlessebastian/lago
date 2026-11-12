/* Captura de endpoints para documentar la FCBQ. Lo ejecuta una PERSONA en su navegador.
 *
 * Uso:
 *  1. Abre basquetcatala.cat, DevTools (F12) -> pestaña Console.
 *  2. Pega este fichero entero y pulsa Enter.
 *  3. Navega a mano (busca un club, abre un partido, sus estadísticas, un PDF de resultados).
 *     Una carga completa de página reinicia la consola: vuelve a pegar el script en cada página;
 *     lo capturado se acumula en localStorage.
 *  4. Al terminar, escribe  __capture.dump()  -> copia un JSON al portapapeles. Pégalo en el chat.
 *     (__capture.reset() borra lo acumulado.)
 *
 * Privacidad: NO guarda cookies, cabeceras, tokens ni valores de parámetros (solo sus nombres),
 * ni contenido de las respuestas: de las JSON solo guarda las claves de primer nivel.
 * No hace ninguna petición propia: solo observa las que hace la página. No resuelve captchas.
 */
(() => {
  const KEY = "__capture_v1";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } };
  const save = (s) => { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {} };
  const state = load();
  state.hits = state.hits || {};
  state.pages = state.pages || {};

  const clean = (u) => {
    try {
      const x = new URL(u, location.href);
      const keys = [...new Set([...x.searchParams.keys()])].sort();
      return x.origin + x.pathname + (keys.length ? "?" + keys.map((k) => k + "=…").join("&") : "");
    } catch { return String(u).slice(0, 200); }
  };
  const rec = (kind, url, method, status, ctype, extra) => {
    const k = [kind, method || "GET", clean(url), status].join(" ");
    const h = (state.hits[k] = state.hits[k] || { kind, method: method || "GET", url: clean(url), status, contentType: ctype || null, count: 0 });
    h.count++; Object.assign(h, extra || {});
    save(state);
  };
  const shape = (txt) => { try { const j = JSON.parse(txt); return Array.isArray(j) ? { jsonArrayOf: j[0] && typeof j[0] === "object" ? Object.keys(j[0]) : typeof j[0], length: j.length } : { jsonKeys: Object.keys(j) }; } catch { return {}; } };

  const of = window.fetch;
  window.fetch = async function (...a) {
    const res = await of.apply(this, a);
    try {
      const url = typeof a[0] === "string" ? a[0] : a[0].url;
      const ct = res.headers.get("content-type") || "";
      const ex = /json/i.test(ct) ? shape(await res.clone().text()) : {};
      rec("fetch", url, (a[1] && a[1].method) || "GET", res.status, ct, ex);
    } catch {}
    return res;
  };
  const xo = XMLHttpRequest.prototype.open, xs = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) { this.__m = m; this.__u = u; return xo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function () {
    this.addEventListener("loadend", () => {
      try {
        const ct = this.getResponseHeader("content-type") || "";
        const ex = /json/i.test(ct) && typeof this.responseText === "string" ? shape(this.responseText) : {};
        rec("xhr", this.__u, this.__m, this.status, ct, ex);
      } catch {}
    });
    return xs.apply(this, arguments);
  };

  // Recursos ya cargados por esta página (HTML, PDF, scripts, etc.), solo URL sin valores.
  performance.getEntriesByType("resource").forEach((e) => rec("resource:" + e.initiatorType, e.name, "GET", null, null));
  new PerformanceObserver((l) => l.getEntries().forEach((e) => rec("resource:" + e.initiatorType, e.name, "GET", null, null)))
    .observe({ type: "resource", buffered: false });

  // Enlaces y formularios de la página actual (estructura de rutas, sin valores de query).
  const links = [...new Set([...document.querySelectorAll("a[href]")].map((a) => clean(a.href)))]
    .filter((u) => u.startsWith(location.origin)).slice(0, 300);
  const forms = [...document.forms].map((f) => ({ action: clean(f.action), method: f.method, fields: [...f.elements].map((e) => e.name).filter(Boolean) }));
  state.pages[clean(location.href)] = { title: document.title, links, forms, hasCaptcha: !!document.querySelector('iframe[src*="recaptcha"],.g-recaptcha') };
  save(state);

  window.__capture = {
    dump() { const s = JSON.stringify({ hits: Object.values(state.hits), pages: state.pages }, null, 1); try { copy(s); console.log("Copiado al portapapeles (" + s.length + " bytes)"); } catch { console.log(s); } return s.length; },
    reset() { localStorage.removeItem(KEY); console.log("borrado"); },
  };
  console.log("Captura activa. Navega y al final ejecuta __capture.dump()");
})();
