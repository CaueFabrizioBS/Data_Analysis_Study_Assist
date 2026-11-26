"""Gera a fonte "Letra do Caue" a partir das folhas do Calligraphr preenchidas à mão.

Uso:  python build/fonte_caue.py
Entrada: build/fontes/calligraphr_p1.jpg e calligraphr_p2.jpg
Saída:   build/fontes/LetraCaue.ttf (+ build/fontes/amostra.png para conferir)

Como funciona: a folha é uma grade fixa (8 colunas, 8 linhas por página). Cada
célula tem uma faixa de rótulo em cima e a área de desenho embaixo, com linhas-guia
cinza claro. A tinta (azul escuro) é separada por limiar, contornada com OpenCV e
vira contorno TrueType. A linha de base da célula vira o y = 0 da fonte.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

HERE = Path(__file__).parent / "fontes"
PAGES = [HERE / "calligraphr_p1.jpg", HERE / "calligraphr_p2.jpg"]
OUT = HERE / "LetraCaue.ttf"

# geometria da grade (px na imagem 1440x2036)
COLS = [34, 206, 378, 550, 722, 894, 1066, 1238, 1410]
AREA_TOP = [148, 371, 594, 818, 1042, 1265, 1489, 1712]
AREA_H = 187
BASELINE_PX = 125.5          # dentro da área de desenho
CAP_PX = 28.5                # linha de cima (altura das maiúsculas)
XH_PX = 65.5                 # altura do x
INK_MAX = 140                # mais escuro que isso é tinta
UP = 3                       # amplia antes de contornar, para suavizar

UPM = 1000
S = 700 / (BASELINE_PX - CAP_PX)   # unidades por px: maiúscula = 700
SIDE = 45                          # margem lateral de cada letra
SPACE = 300

P1 = list("!\"#$%&") + list("'()*+,") + list("-./01234") + list("56789:;<") + \
    list("=>?@ABCD") + list("EFGHIJKL") + list("MNOPQRST") + list("UVWXYZ[\\")
P2 = list("]^_`ab") + list("cdefgh") + list("ijklmnop") + list("qrstuvwx") + \
    list("yz{|}~ªº") + list("¿àáçéêìí") + list("óõú•")


def cells(page_chars, first_rows_six=True):
    """Gera (char, linha, coluna) seguindo a ordem da folha."""
    out, r, c = [], 0, 0
    for ch in page_chars:
        out.append((ch, r, c))
        c += 1
        limit = 6 if r < 2 and first_rows_six else 8
        if c >= limit:
            r, c = r + 1, 0
    return out


def contours_of(img_gray, r, c):
    """Contornos da tinta de uma célula, em px da célula (y para baixo)."""
    y0, x0 = AREA_TOP[r], COLS[c]
    crop = img_gray[y0 + 3:y0 + AREA_H - 3, x0 + 4:COLS[c + 1] - 4]
    crop = cv2.GaussianBlur(crop, (3, 3), 0)
    big = cv2.resize(crop, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    mask = (big < INK_MAX).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    res = []
    if hier is None:
        return res
    for cnt, h in zip(cnts, hier[0]):
        area = cv2.contourArea(cnt)
        is_hole = h[3] != -1
        if area < (25 if is_hole else 60):          # sujeira de JPEG
            continue
        approx = cv2.approxPolyDP(cnt, 1.2, True)
        pts = [(p[0][0] / UP + 4, p[0][1] / UP + 3) for p in approx]
        if len(pts) >= 3:
            res.append({"pts": pts, "hole": is_hole})
    return res


def bbox(conts):
    xs = [x for k in conts for x, _ in k["pts"]]
    ys = [y for k in conts for _, y in k["pts"]]
    return min(xs), min(ys), max(xs), max(ys)


def shift(conts, dx=0.0, dy=0.0):
    return [{"pts": [(x + dx, y + dy) for x, y in k["pts"]], "hole": k["hole"]} for k in conts]


def signed_area(pts):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        a += x1 * y2 - x2 * y1
    return a / 2


def to_glyph(conts):
    """px da célula -> unidades da fonte; devolve (glyph, avanço)."""
    if not conts:
        return None, SPACE
    x0, _, x1, _ = bbox(conts)
    pen = TTGlyphPen(None)
    for k in conts:
        pts = [((x - x0) * S + SIDE, (BASELINE_PX - y) * S) for x, y in k["pts"]]
        a = signed_area(pts)
        # TrueType: contorno externo no sentido horário (área negativa), furo anti-horário
        if (not k["hole"] and a > 0) or (k["hole"] and a < 0):
            pts = pts[::-1]
        pen.moveTo((round(pts[0][0]), round(pts[0][1])))
        for x, y in pts[1:]:
            pen.lineTo((round(x), round(y)))
        pen.closePath()
    return pen.glyph(), round((x1 - x0) * S + 2 * SIDE)


def split_accent(conts, above_px):
    """Separa o acento (peças externas que começam acima de above_px) do corpo.

    O corpo é a maior peça externa e os furos dela; o resto que começa acima
    da altura do x é acento (ou pingo do i)."""
    outers = [k for k in conts if not k["hole"]]
    if len(outers) < 2:
        return [], conts
    body = max(outers, key=lambda k: abs(signed_area(k["pts"])))
    acc = [k for k in outers if k is not body and min(y for _, y in k["pts"]) < above_px]
    return acc, [k for k in conts if k not in acc]


def split_below(conts, below_px):
    low = [k for k in conts if min(y for _, y in k["pts"]) > below_px]
    return low, [k for k in conts if k not in low]


def place_accent(base, acc, gap_px=6):
    """Centraliza o acento em cima da letra base."""
    if not acc:
        return base
    bx0, by0, bx1, _ = bbox(base)
    ax0, _, ax1, ay1 = bbox(acc)
    dx = (bx0 + bx1) / 2 - (ax0 + ax1) / 2
    dy = (by0 - gap_px) - ay1
    return base + shift(acc, dx, dy)


def main():
    glyphs = {}
    for path, chars, first6 in [(PAGES[0], P1, True), (PAGES[1], P2, True)]:
        gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        for ch, r, c in cells(chars, first6):
            glyphs[ch] = contours_of(gray, r, c)

    # acentos soltos, tirados das letras acentuadas que existem na folha
    acc = {}
    acc["acute"], _ = split_accent(glyphs["á"], XH_PX - 2)
    acc["grave"], _ = split_accent(glyphs["à"], XH_PX - 2)
    acc["circ"], _ = split_accent(glyphs["ê"], XH_PX - 2)
    acc["tilde"], _ = split_accent(glyphs["õ"], XH_PX - 2)
    cedilha, _ = split_below(glyphs["ç"], BASELINE_PX - 4)
    if not cedilha:
        # a cedilha está grudada no c: recorta só a tinta abaixo da linha de base
        gray = cv2.imread(str(PAGES[1]), cv2.IMREAD_GRAYSCALE)
        ch, r, c = next(x for x in cells(P2) if x[0] == "ç")
        y0, x0 = AREA_TOP[r], COLS[c]
        cut = int(BASELINE_PX) + 2
        crop = gray[y0 + cut:y0 + AREA_H - 3, x0 + 4:COLS[c + 1] - 4]
        big = cv2.resize(cv2.GaussianBlur(crop, (3, 3), 0), None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
        mask = (big < INK_MAX).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in cnts:
            if cv2.contourArea(cnt) >= 40:
                approx = cv2.approxPolyDP(cnt, 1.2, True)
                cedilha.append({"pts": [(p[0][0] / UP + 4, p[0][1] / UP + cut) for p in approx], "hole": False})

    compostos = {
        "ã": ("a", "tilde"), "â": ("a", "circ"), "ô": ("o", "circ"), "è": ("e", "grave"),
        "ò": ("o", "grave"), "ù": ("u", "grave"), "î": ("i", "circ"),
        "Á": ("A", "acute"), "À": ("A", "grave"), "Â": ("A", "circ"), "Ã": ("A", "tilde"),
        "É": ("E", "acute"), "Ê": ("E", "circ"), "Í": ("I", "acute"), "Ó": ("O", "acute"),
        "Ô": ("O", "circ"), "Õ": ("O", "tilde"), "Ú": ("U", "acute"),
    }
    for novo, (base, a) in compostos.items():
        b = glyphs[base]
        if base in "iI":
            # tira o pingo do i antes de por o acento
            dot, b = split_accent(b, XH_PX - 2) if base == "i" else ([], b)
        glyphs[novo] = place_accent(b, acc[a], gap_px=8 if base.isupper() else 6)
    if cedilha:
        cb = glyphs["C"]
        bx0, _, bx1, by1 = bbox(cb)
        cx0, cy0, cx1, _ = bbox(cedilha)
        glyphs["Ç"] = cb + shift(cedilha, (bx0 + bx1) / 2 - (cx0 + cx1) / 2, by1 + 1 - cy0)

    # equivalentes tipográficos
    glyphs["“"] = glyphs["”"] = glyphs['"']
    glyphs["‘"] = glyphs["’"] = glyphs["'"]
    glyphs["–"] = glyphs["-"]
    glyphs["×"] = glyphs["x"]
    glyphs[" "] = []
    glyphs[" "] = []

    order = [".notdef"] + sorted({f"uni{ord(ch):04X}" for ch in glyphs})
    cmap = {ord(ch): f"uni{ord(ch):04X}" for ch in glyphs}
    tt_glyphs, metrics = {}, {}
    pen = TTGlyphPen(None)
    pen.moveTo((60, 0)); pen.lineTo((60, 700)); pen.lineTo((440, 700)); pen.lineTo((440, 0)); pen.closePath()
    tt_glyphs[".notdef"], metrics[".notdef"] = pen.glyph(), (500, 60)
    for ch, conts in glyphs.items():
        name = f"uni{ord(ch):04X}"
        if name in tt_glyphs:
            continue
        g, adv = to_glyph(conts)
        if g is None:
            g = TTGlyphPen(None).glyph()
        tt_glyphs[name] = g
        metrics[name] = (adv, SIDE if conts else 0)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(tt_glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=950, descent=-300)
    fb.setupNameTable({"familyName": "Letra do Caue", "styleName": "Regular",
                       "uniqueFontIdentifier": "LetraCaue-Regular", "fullName": "Letra do Caue",
                       "psName": "LetraCaue-Regular", "version": "Version 1.0"})
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-300, sTypoLineGap=100,
                usWinAscent=1000, usWinDescent=320, sxHeight=round((BASELINE_PX - XH_PX) * S),
                sCapHeight=700, fsType=0)
    fb.setupPost()
    fb.save(OUT)
    print(f"ok: {OUT.name} com {len(cmap)} caracteres")


if __name__ == "__main__":
    main()
