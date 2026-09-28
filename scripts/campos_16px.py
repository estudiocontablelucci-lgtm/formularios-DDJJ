"""Campos de los cuatro formularios a 16px.

Safari de iPhone hace zoom al enfocar un input, select o textarea con letra menor
a 16px, y el formulario queda corrido hasta que el cliente lo achica a mano. Los
campos estaban en 15px y la línea de firma en 14px.

Trabaja por selector, sólo dentro del <style>:
  - la regla común de campos (input[type=text|email|number|date], textarea, select)
  - .firma-campo input

Uso:
  python scripts/campos_16px.py           # aplica
  python scripts/campos_16px.py --check   # en seco: dice qué cambiaría
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORMULARIOS = ["mono", "bp", "iigg", "sas"]

# Regla común: arranca en input[type="text"], y termina en la primera llave de cierre.
REGLA_CAMPOS = re.compile(r'(  input\[type="text"\],\s*\n(?:  [^{\n]+,\s*\n)*  select \{[^}]*?)font-size: 15px;')
FIRMA = re.compile(r"(\.firma-campo input \{[^}]*?)font-size: 14px;")


def transformar(texto: str) -> tuple[str, list[str]]:
    cambios: list[str] = []
    texto, n = REGLA_CAMPOS.subn(r"\1font-size: 16px;", texto)
    if n != 1:
        raise ValueError(f"regla común de campos: se esperaba 1 y hay {n}")
    cambios.append("campos 15px -> 16px")
    texto, n = FIRMA.subn(r"\1font-size: 16px;", texto)
    if n != 1:
        raise ValueError(f".firma-campo input: se esperaba 1 y hay {n}")
    cambios.append("firma 14px -> 16px")
    return texto, cambios


def main() -> None:
    en_seco = "--check" in sys.argv
    for nombre in FORMULARIOS:
        ruta = RAIZ / nombre / "index.html"
        crudo = ruta.read_bytes()
        eol = "\r\n" if b"\r\n" in crudo else "\n"
        texto = ruta.read_text(encoding="utf-8")
        nuevo, cambios = transformar(texto)
        print(f"{nombre}: {', '.join(cambios)}")
        if not en_seco:
            ruta.write_text(nuevo, encoding="utf-8", newline=eol)
    if en_seco:
        print("(en seco: no se escribió nada)")


if __name__ == "__main__":
    main()
