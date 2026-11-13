#!/usr/bin/env python3
"""Valida contraste WCAG AA dos 5 temas (claro e escuro) lendo tokens.css.

Texto normal >= 4,5:1; elementos de UI >= 3:1. Sai com código 1 se algum par falhar.
Uso: python3 contraste.py [--tudo]   (--tudo lista todos os pares, não só o menor por tema)
"""
import re
import sys
from pathlib import Path

TOKENS = Path(__file__).with_name("tokens.css")
TEXTO, UI = 4.5, 3.0

# (primeiro plano, fundo, mínimo, descrição). "mix:x" = x a 14% sobre a superfície.
SUPERFICIES = ("fundo", "superficie", "superficie-2")
PARES = (
    [("texto", s, TEXTO, "texto") for s in SUPERFICIES]
    + [("texto-suave", s, TEXTO, "texto suave") for s in SUPERFICIES]
    + [("primaria-texto", s, TEXTO, "link/primária como texto") for s in SUPERFICIES]
    + [("acento-texto", s, TEXTO, "acento como texto") for s in SUPERFICIES]
    + [(e, s, TEXTO, f"estado {e}") for e in ("sucesso", "erro", "aviso") for s in SUPERFICIES]
    + [(e, f"mix:{e}", TEXTO, f"estado {e} sobre seu fundo suave") for e in ("sucesso", "erro", "aviso")]
    + [("texto", f"mix:{e}", TEXTO, f"texto sobre fundo suave de {e}") for e in ("sucesso", "erro", "aviso")]
    + [("sobre-primaria", "primaria", TEXTO, "texto do botão primário")]
    + [("sobre-acento", "acento", TEXTO, "texto do botão de acento")]
    + [("primaria", "fundo", UI, "botão primário x fundo"), ("primaria", "superficie", UI, "botão primário x superfície")]
    + [("borda-forte", "fundo", UI, "borda de campo x fundo"), ("borda-forte", "superficie", UI, "borda de campo x superfície")]
)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def misturar(fg, bg, p=0.14):
    return tuple(round(f * p + b * (1 - p)) for f, b in zip(fg, bg))


def ler_temas(css):
    """{tema: {modo: {token: rgb}}} a partir de `--cor-x: light-dark(#a, #b);`."""
    temas = {}
    for bloco in re.finditer(r'(\[data-tema="(\d)"\][^{]*)\{([^}]*)\}', css):
        n = int(bloco.group(2))
        modos = {"claro": {}, "escuro": {}}
        for nome, a, b in re.findall(r"--cor-([\w-]+):\s*light-dark\((#[0-9a-fA-F]{6}),\s*(#[0-9a-fA-F]{6})\)", bloco.group(3)):
            modos["claro"][nome], modos["escuro"][nome] = hex_rgb(a), hex_rgb(b)
        temas[n] = modos
    return temas


def verificar(temas):
    resultados = []  # (tema, modo, desc, fg, bg, razao, minimo)
    erros = []
    for n in range(1, 6):
        if n not in temas or not temas[n]["claro"]:
            erros.append(f"tema {n} ausente em tokens.css")
            continue
        for modo, cores in temas[n].items():
            for fg, bg, minimo, desc in PARES:
                try:
                    cf = cores[fg]
                    if bg.startswith("mix:"):
                        cb = misturar(cores[bg[4:]], cores["superficie"])
                    else:
                        cb = cores[bg]
                except KeyError as e:
                    erros.append(f"tema {n} {modo}: token --cor-{e.args[0]} ausente")
                    continue
                resultados.append((n, modo, f"{desc} ({fg} / {bg})", cf, cb, razao(cf, cb), minimo))
    return resultados, erros


def main():
    resultados, erros = verificar(ler_temas(TOKENS.read_text(encoding="utf-8")))
    falhas = [r for r in resultados if r[5] < r[6]]
    tudo = "--tudo" in sys.argv
    for e in erros:
        print("ERRO:", e)
    print(f"{'tema':<5}{'modo':<8}{'menor razão':<13}par")
    for n in range(1, 6):
        for modo in ("claro", "escuro"):
            rs = [r for r in resultados if r[0] == n and r[1] == modo]
            if rs:
                m = min(rs, key=lambda r: r[5] / r[6])
                print(f"{n:<5}{modo:<8}{m[5]:<13.2f}{m[2]} (mín. {m[6]})")
    if tudo:
        for r in resultados:
            print(f"  t{r[0]} {r[1]:<6} {r[5]:5.2f} >= {r[6]}  {r[2]}")
    for r in falhas:
        print(f"FALHA t{r[0]} {r[1]}: {r[2]} = {r[5]:.2f} < {r[6]}")
    print(f"{len(resultados)} pares verificados, {len(falhas)} falhas, {len(erros)} erros")
    return 1 if (falhas or erros) else 0


if __name__ == "__main__":
    sys.exit(main())
