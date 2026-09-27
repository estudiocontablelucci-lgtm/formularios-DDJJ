"""Comprueba que un cambio de estilo no toco nada funcional de los formularios.

Compara la landing y los cuatro formularios del working tree contra una base y
falla si cambio algo que un cambio visual no deberia tocar:

1. Los <script> (inline y externos) tienen que ser identicos byte a byte.
2. Fuera del contenido de <style> y del <link> de Google Fonts, el archivo tiene
   que ser identico byte a byte: mismos name, id, for, required, value, onclick,
   oninput, placeholders y copy.
3. Si (2) no se cumple, compara elemento por elemento ignorando solo `class` y
   `style` (el caso de agregarle una clase a un campo) y muestra la primera
   diferencia. Cualquier otra diferencia es una falla.

Base:
  --ref REF   una ref de git (por defecto `main`). Con autocrlf el index guarda
              LF y el working tree CRLF: en este modo se normaliza el fin de linea.
  --base DIR  un directorio con copias de los archivos: comparacion cruda, sin
              normalizar nada.

Uso:  python scripts/verificar_solo_estilo.py [--ref main | --base DIR]
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVOS = ("index.html", "mono/index.html", "bp/index.html", "iigg/index.html", "sas/index.html")

SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)
STYLE = re.compile(r"(<style\b[^>]*>).*?(</style>)", re.S | re.I)
LINK_FUENTES = re.compile(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">')
IGNORADOS = {"class", "style"}


class Huella(HTMLParser):
    """Secuencia de etiquetas, atributos (menos class/style) y texto, sin el <style>."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.eventos: list[tuple] = []
        self._en_style = False

    def _abre(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "style":
            self._en_style = True
            return
        d = dict(attrs)
        if tag == "link" and (d.get("href") or "").startswith("https://fonts.googleapis.com/css2"):
            return
        self.eventos.append(("<", tag, tuple((k, v) for k, v in attrs if k not in IGNORADOS)))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._abre(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._abre(tag, attrs)
        if tag == "style":
            self._en_style = False

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._en_style = False
            return
        self.eventos.append(("</", tag))

    def handle_data(self, data: str) -> None:
        if not self._en_style:
            self.eventos.append(("txt", data))

    def handle_entityref(self, name: str) -> None:
        self.eventos.append(("&", name))

    def handle_charref(self, name: str) -> None:
        self.eventos.append(("&#", name))

    def handle_comment(self, data: str) -> None:
        if not self._en_style:
            self.eventos.append(("<!--", data))

    def handle_decl(self, decl: str) -> None:
        self.eventos.append(("<!", decl))


def huella(texto: str) -> list[tuple]:
    p = Huella()
    p.feed(texto)
    p.close()
    return p.eventos


def sin_estilo(texto: str) -> str:
    texto = STYLE.sub(r"\1\2", texto)
    return LINK_FUENTES.sub("<link fuentes>", texto)


def leer_base(rel: str, ref: str | None, base: Path | None) -> str:
    if base is not None:
        return (base / rel).read_bytes().decode("utf-8")
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=REPO, capture_output=True)
    if r.returncode:
        sys.exit(f"git show {ref}:{rel} fallo: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout.decode("utf-8")


def verificar(rel: str, ref: str | None, base: Path | None) -> bool:
    antes = leer_base(rel, ref, base)
    ahora = (REPO / rel).read_bytes().decode("utf-8")
    if base is None:  # git: el index puede tener LF y el working tree CRLF
        antes, ahora = antes.replace("\r\n", "\n"), ahora.replace("\r\n", "\n")

    ok = True
    s_antes, s_ahora = SCRIPT.findall(antes), SCRIPT.findall(ahora)
    if s_antes == s_ahora:
        digest = hashlib.sha256("".join(s_ahora).encode("utf-8")).hexdigest()[:12]
        linea_js = f"{len(s_ahora)} <script> identicos (sha256 {digest})"
    else:
        ok = False
        linea_js = f"<script> DISTINTOS ({len(s_antes)} antes, {len(s_ahora)} ahora)"

    if sin_estilo(antes) == sin_estilo(ahora):
        linea_html = "fuera de <style> y <link> de fuentes: identico"
    else:
        h_antes, h_ahora = huella(antes), huella(ahora)
        if h_antes == h_ahora:
            linea_html = "difiere solo en class/style de algun elemento (permitido)"
        else:
            ok = False
            i = next((i for i, (a, b) in enumerate(zip(h_antes, h_ahora)) if a != b),
                     min(len(h_antes), len(h_ahora)))
            antes_i = repr(h_antes[i])[:300] if i < len(h_antes) else "(fin)"
            ahora_i = repr(h_ahora[i])[:300] if i < len(h_ahora) else "(fin)"
            linea_html = f"CAMBIO FUNCIONAL en el evento {i}:\n      antes: {antes_i}\n      ahora: {ahora_i}"

    if antes == ahora:
        nota = "archivo sin ningun cambio"
    else:
        nota = "cambio solo lo visual" if ok else "revisar"
    print(f"  {'OK  ' if ok else 'FALLA'} {rel} ({nota})\n      {linea_js}\n      {linea_html}")
    return ok


def main() -> None:
    # La consola de Windows es cp1252: el JS y el copy traen caracteres que no mapea.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    ref: str | None = "main"
    base: Path | None = None
    if "--base" in args:
        base, ref = Path(args[args.index("--base") + 1]), None
    elif "--ref" in args:
        ref = args[args.index("--ref") + 1]
    print(f"Base: {base if base else 'git ' + ref}")
    resultados = [verificar(rel, ref, base) for rel in ARCHIVOS]
    if not all(resultados):
        sys.exit("Hay cambios funcionales: revisar antes de publicar.")
    print("Sin cambios funcionales.")


if __name__ == "__main__":
    main()
