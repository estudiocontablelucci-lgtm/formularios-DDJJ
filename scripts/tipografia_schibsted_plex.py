"""Tipografia de estudiolucci.com.ar (sep 2026) en la landing y los cuatro formularios.

- Schibsted Grotesk para todo el texto: reemplaza a Outfit, y a Spectral en los
  titulos. Titulos en 600, tracking -0.015em, line-height 1.2.
- IBM Plex Sans con digitos tabulares para las cifras: montos, porcentajes,
  cantidades, fechas, CUIT, DNI, CBU, telefonos y el % de avance.
- Spectral 600 queda solo para el wordmark "Lucci & Asociados" del header.

Toca unicamente el <link> de Google Fonts y el bloque <style>. El resto del
archivo sale igual byte a byte; lo comprueba scripts/verificar_solo_estilo.py.

Uso:  python scripts/tipografia_schibsted_plex.py [--check]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FORMULARIOS = ("mono", "bp", "iigg", "sas")

LINK_VIEJO = (
    '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400'
    '&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">'
)
# Spectral solo en el peso del wordmark. La landing no tiene wordmark ni cifras.
LINK_FORMULARIO = (
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600'
    '&family=Schibsted+Grotesk:wght@400;500;600;700&family=Spectral:wght@600&display=swap" rel="stylesheet">'
)
LINK_LANDING = (
    '<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700'
    '&display=swap" rel="stylesheet">'
)

TITULO = "letter-spacing: -0.015em; line-height: 1.2;"

VARIABLES_VIEJAS = (
    "    --serif:   'Spectral', Georgia, serif;\n"
    "    --sans:    'Outfit', system-ui, sans-serif;\n"
)
VARIABLES_NUEVAS = (
    "    /* Tipografía de estudiolucci.com.ar (sep 2026) */\n"
    "    --font-sans: 'Schibsted Grotesk', system-ui, sans-serif;  /* todo el texto */\n"
    "    --font-num:  'IBM Plex Sans', system-ui, sans-serif;      /* cifras */\n"
    "    --font-logo: 'Spectral', Georgia, serif;                  /* sólo el wordmark */\n"
)

# Mismo bloque en los cuatro: el aspecto es comun aunque el JS no lo sea.
# Va al final del <style> para ganarle a `.firma-campo input` y a los
# `input[type=...]`, que tienen la misma especificidad.
BLOQUE_CIFRAS = """
  /* CIFRAS: IBM Plex Sans con dígitos tabulares en lo que se tipea o se lee como
     número. Va por atributo y no por clase porque parte de los campos los arma el
     JS (socios de sas, jurisdicciones de mono) y un cambio de estilo no toca el JS.
     Los montos se reconocen por el placeholder de moneda ($, USD, EUR).
     Direcciones, patentes, pólizas y números de inscripción quedan en la letra del texto. */
  .progress-text,
  .reparto .valor,
  input[type="number"],
  input[type="date"],
  input[inputmode="numeric"],
  input[inputmode="decimal"],
  input[placeholder^="$"],
  input[placeholder^="USD"],
  input[placeholder^="EUR"],
  input[name*="fecha"],
  input[name*="porcentaje"],
  input[name$="_gastos_venta"],
  input[name*="cuit"],
  input[name$="_dni"],
  input[name="cbu"],
  input[name="telefono"],
  input[name$="_celular"] {
    font-family: var(--font-num);
    font-variant-numeric: tabular-nums;
  }
"""

# sas ya tenia el capital en tabular; el bloque de cifras lo cubre (inputmode="numeric").
MONTO_SAS = (
    "\n  /* El monto de capital se lee mejor en tabular */\n"
    "  input.monto { font-variant-numeric: tabular-nums; }\n"
)

STYLE = re.compile(r"(<style>)(.*?)(</style>)", re.S)


class Falla(Exception):
    pass


def reemplazar(texto: str, viejo: str, nuevo: str, donde: str, veces: int = 1) -> str:
    n = texto.count(viejo)
    if n != veces:
        raise Falla(f"{donde}: esperaba {veces} ocurrencia(s) de {viejo[:60]!r}, hay {n}")
    return texto.replace(viejo, nuevo)


def titulo(css: str, selector: str, donde: str) -> str:
    """Un titulo de una linea: Spectral -> Schibsted, mas tracking y line-height."""
    patron = re.compile(
        r"(  " + re.escape(selector) + r" \{ )font-family: var\(--serif\);([^}\n]*?font-weight: 600;)"
    )
    css, n = patron.subn(lambda m: f"{m.group(1)}font-family: var(--font-sans);{m.group(2)} {TITULO}", css)
    if n != 1:
        raise Falla(f"{donde}: el titulo {selector!r} aparece {n} veces, esperaba 1")
    return css


def css_formulario(css: str, form: str) -> str:
    css = reemplazar(css, VARIABLES_VIEJAS, VARIABLES_NUEVAS, form)
    css = reemplazar(
        css, ".header-text h1 { font-family: var(--serif);",
        ".header-text h1 { font-family: var(--font-logo);", form,
    )
    titulos = [".intro-box h2", ".section-letter", ".section-title", ".firma-box h3"]
    if form in ("bp", "iigg"):
        titulos.append(".sub-section-title")
    for sel in titulos:
        css = titulo(css, sel, form)

    # "Inmueble 1", "Rodado 2": rotulo de tarjeta, mismo tratamiento que .socio-num
    # y .jurisdiccion-num (15px, 500). Mantiene --muted.
    if form == "bp":
        css = reemplazar(
            css,
            "  .slot-card-title { font-family: var(--serif); font-size: .9rem; color: var(--muted); font-weight: 400; }",
            "  .slot-card-title { font-size: 15px; color: var(--muted); font-weight: 500; }",
            form,
        )
    if form == "iigg":
        css = reemplazar(
            css,
            "  .slot-card-title {\n    font-family: var(--serif);\n    font-size: .9rem;\n"
            "    color: var(--muted);\n    font-weight: 400;\n  }",
            "  .slot-card-title {\n    font-size: 15px;\n    color: var(--muted);\n    font-weight: 500;\n  }",
            form,
        )
    if form == "sas":
        css = reemplazar(css, MONTO_SAS, "", form)

    css = css.replace("var(--sans)", "var(--font-sans)")

    for resto in ("var(--serif)", "var(--sans)", "Outfit"):
        if resto in css:
            raise Falla(f"{form}: quedo {resto!r} en el <style>")

    return css.rstrip(" \n") + "\n" + BLOQUE_CIFRAS


def css_landing(css: str) -> str:
    donde = "landing"
    css = reemplazar(
        css, "    --radius: 10px;\n  }",
        "    --radius: 10px;\n    --font-sans: 'Schibsted Grotesk', system-ui, sans-serif;\n  }", donde,
    )
    css = reemplazar(css, "font-family: 'Outfit', sans-serif;", "font-family: var(--font-sans);", donde)
    css = reemplazar(
        css,
        ".header h1 { font-family: 'Spectral', serif; font-size: 1.75rem; font-weight: 600; margin-bottom: .25rem; }",
        f".header h1 {{ font-family: var(--font-sans); font-size: 1.75rem; font-weight: 600; {TITULO} margin-bottom: .25rem; }}",
        donde,
    )
    css = reemplazar(
        css,
        ".card-title { font-family: 'Spectral', serif; font-size: 1.15rem; font-weight: 600; margin-bottom: .2rem; }",
        f".card-title {{ font-family: var(--font-sans); font-size: 1.15rem; font-weight: 600; {TITULO} margin-bottom: .2rem; }}",
        donde,
    )
    for resto in ("Outfit", "Spectral"):
        if resto in css:
            raise Falla(f"{donde}: quedo {resto!r} en el <style>")
    return css


def procesar(rel: str, check: bool) -> bool:
    ruta = REPO / rel
    crudo = ruta.read_bytes()
    # Se preserva el fin de linea del working tree (CRLF con autocrlf).
    crlf = crudo.count(b"\r\n")
    if crlf and crlf != crudo.count(b"\n"):
        raise Falla(f"{rel}: fines de linea mezclados, no se toca")
    texto = crudo.decode("utf-8").replace("\r\n", "\n")

    es_landing = rel == "index.html"
    link_nuevo = LINK_LANDING if es_landing else LINK_FORMULARIO
    if link_nuevo in texto:
        print(f"  {rel}: sin cambios (ya estaba)")
        return False

    texto = reemplazar(texto, LINK_VIEJO, link_nuevo, rel)
    estilos = STYLE.findall(texto)
    if len(estilos) != 1:
        raise Falla(f"{rel}: esperaba un solo <style>, hay {len(estilos)}")
    abre, css, cierra = estilos[0]
    css_nuevo = css_landing(css) if es_landing else css_formulario(css, rel.split("/")[0])
    texto = texto.replace(abre + css + cierra, abre + css_nuevo + cierra, 1)

    if crlf:
        texto = texto.replace("\n", "\r\n")
    print(f"  {rel}: link de fuentes + <style>")
    if not check:
        ruta.write_bytes(texto.encode("utf-8"))
    return True


def main() -> None:
    check = "--check" in sys.argv
    print("Tipografia Schibsted + Plex" + (" (--check, no escribe)" if check else ""))
    archivos = ["index.html"] + [f"{f}/index.html" for f in FORMULARIOS]
    try:
        for rel in archivos:
            procesar(rel, check)
    except Falla as e:
        sys.exit(f"ERROR {e}")


if __name__ == "__main__":
    main()
