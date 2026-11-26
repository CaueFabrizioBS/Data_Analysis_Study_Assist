"""Gera os desenhos SVG de build/desenhos/. Rode: python build/gerar_desenhos.py"""
import random
from pathlib import Path

OUT = Path(__file__).parent / "desenhos"
OUT.mkdir(exist_ok=True)
H = 'font-family="Letra do Caue, Ink Free, Segoe Print, cursive"'
B, R, G, Y, P, K = "#2b59c3", "#e0453a", "#2f9e44", "#f2b705", "#8e44ad", "#1f2430"


def svg(vb, width, body):
    return f'<svg viewBox="{vb}" width="{width}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def t(x, y, s, c=K, size=16, anchor="start"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" {H} fill="{c}">{s}</text>'


files = {}

# 1. índices de string
w = "PARALELO"
s = t(8, 50, "+", G, 15) + t(8, 128, "−", R, 15)
for i, ch in enumerate(w):
    x = 40 + i * 54
    s += f'<rect x="{x}" y="60" width="46" height="46" rx="8" fill="#fff" stroke="{B}" stroke-width="2.5"/>'
    s += t(x + 23, 92, ch, K, 24, "middle") + t(x + 23, 50, i, G, 17, "middle") + t(x + 23, 128, i - len(w), R, 17, "middle")
s += f'<path d="M148 150 q0 14 14 14 h96 q14 0 14 -14" fill="none" stroke="{P}" stroke-width="2.5" stroke-linecap="round"/>'
s += t(210, 186, "word[2:5] → 'RAL'  (o 5 fica de fora)", P, 17, "middle")
files["indices"] = svg("0 0 480 195", 470, s)

# 2. for como esteira
s = f'<path d="M10 120 H290" stroke="{K}" stroke-width="3" stroke-linecap="round"/>'
for cx in (30, 150, 270):
    s += f'<circle cx="{cx}" cy="130" r="8" fill="none" stroke="{K}" stroke-width="2.5"/>'
for i, item in enumerate(["scifi", "drama", "thriller"]):
    x = 20 + i * 86
    s += f'<rect x="{x}" y="70" width="74" height="40" rx="8" fill="#eef4ff" stroke="{B}" stroke-width="2.5"/>' + t(x + 37, 96, item, K, 16, "middle")
s += f'<path d="M296 90 h40" stroke="{R}" stroke-width="3" stroke-linecap="round"/>'
s += f'<path d="M328 80 l10 10 -10 10" fill="none" stroke="{R}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
s += f'<rect x="350" y="52" width="150" height="76" rx="12" fill="#fffbea" stroke="{Y}" stroke-width="3"/>'
s += t(425, 84, "print(value)", K, 17, "middle") + t(425, 110, "um item por volta", G, 14, "middle")
s += t(150, 40, "for value in film_genres:", B, 17, "middle")
s += f'<path d="M425 138 q0 26 -60 26 h-250 q-40 0 -40 -20" fill="none" stroke="{P}" stroke-width="2" stroke-dasharray="5 6"/>'
s += t(250, 160, "acabou a lista? sai do ciclo", P, 14)
files["for-esteira"] = svg("0 0 520 175", 480, s)

# 3. while elevador
def boneco(cx, c):
    return (f'<circle cx="{cx}" cy="120" r="10" fill="none" stroke="{c}" stroke-width="2.5"/>'
            f'<path d="M{cx} 130 v30 M{cx} 140 l-12 10 M{cx} 140 l12 10 M{cx} 160 l-9 20 M{cx} 160 l9 20" '
            f'stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>')
s = f'<rect x="30" y="20" width="130" height="165" rx="6" fill="#f4f6f9" stroke="{K}" stroke-width="3"/>'
s += f'<path d="M95 20 V185" stroke="{K}" stroke-width="2"/>' + boneco(62, B) + boneco(128, G)
s += f'<rect x="190" y="40" width="200" height="22" rx="11" fill="none" stroke="{K}" stroke-width="2.5"/>'
s += f'<rect x="193" y="43" width="150" height="16" rx="8" fill="{Y}"/>' + t(400, 57, "400 kg")
s += t(190, 95, "while total_weight &lt; capacity:", B, 17) + t(210, 122, "mais uma pessoa entra")
s += t(190, 160, "passou de 400? a condição vira False", R) + t(190, 182, "e o ciclo para", R)
files["while-elevador"] = svg("0 0 520 200", 460, s)

# 4. dicionário como etiquetas
s = ""
for i, (k, v) in enumerate([("Coca-Cola", "45.15"), ("Nike", "97.99"), ("Walmart", "130.68")]):
    y = 30 + i * 52
    s += f'<path d="M30 {y} h110 l18 18 -18 18 h-110 z" fill="#fffbea" stroke="{Y}" stroke-width="2.5" stroke-linejoin="round"/>'
    s += f'<circle cx="142" cy="{y + 18}" r="4" fill="none" stroke="{Y}" stroke-width="2"/>' + t(86, y + 24, k, K, 17, "middle")
    s += f'<path d="M168 {y + 18} h80" stroke="{K}" stroke-width="2" stroke-dasharray="4 5"/>'
    s += f'<rect x="256" y="{y}" width="90" height="36" rx="8" fill="#eef4ff" stroke="{B}" stroke-width="2.5"/>' + t(301, y + 24, v, K, 17, "middle")
s += t(86, 186, "chave", "#b98900", 16, "middle") + t(301, 186, "valor", B, 16, "middle")
s += t(370, 70, "dic['Nike']", R) + t(370, 94, "→ 97.99", R)
s += t(370, 130, "busca pelo nome,", G, 14) + t(370, 150, "não pela posição", G, 14)
files["dicionario"] = svg("0 0 520 195", 470, s)

# 5. anatomia do DataFrame
s = f'<rect x="150" y="40" width="240" height="30" fill="#eef4ff" stroke="{B}" stroke-width="2"/>'
s += t(210, 61, "genre", B, 16, "middle") + t(330, 61, "total play", B, 16, "middle")
for i, (ix, g, tp) in enumerate([("0", "pop", "92.8"), ("1", "jazz", "3.0"), ("2", "rock", "211.9")]):
    y = 70 + i * 30
    s += f'<rect x="100" y="{y}" width="50" height="30" fill="#f0fdf4" stroke="{G}" stroke-width="2"/>' + t(125, y + 21, ix, G, 16, "middle")
    s += f'<rect x="150" y="{y}" width="120" height="30" fill="#fff" stroke="#c3c9d4" stroke-width="1.5"/>'
    s += f'<rect x="270" y="{y}" width="120" height="30" fill="#fff" stroke="#c3c9d4" stroke-width="1.5"/>'
    s += t(210, y + 21, g, K, 16, "middle") + t(330, y + 21, tp, K, 16, "middle")
s += f'<rect x="270" y="70" width="120" height="90" fill="none" stroke="{R}" stroke-width="3" rx="4"/>'
s += t(400, 110, "uma coluna", R) + t(400, 130, "= Series", R)
s += t(125, 30, "índice", G, 16, "middle") + t(270, 25, "nomes das colunas", B, 16, "middle")
s += f'<rect x="96" y="128" width="298" height="34" fill="none" stroke="{P}" stroke-width="2.5" stroke-dasharray="6 5" rx="4"/>'
s += t(96, 188, "uma linha: df.loc[2]", P) + t(290, 188, "df.shape → (3, 2)")
files["dataframe"] = svg("0 0 520 200", 470, s)

# 6. groupby: dividir, aplicar, combinar
def caixa(x, y, linhas, c):
    h = 24 * len(linhas) + 10
    r = f'<rect x="{x}" y="{y}" width="92" height="{h}" rx="8" fill="#fff" stroke="{c}" stroke-width="2.5"/>'
    for j, l in enumerate(linhas):
        r += t(x + 46, y + 26 + 24 * j, l, K, 16, "middle")
    return r
s = t(56, 28, "tabela", B, 16, "middle") + caixa(10, 40, ["2008 · a", "2010 · b", "2008 · c", "2010 · d"], B)
s += caixa(160, 20, ["2008 · a", "2008 · c"], G) + caixa(160, 110, ["2010 · b", "2010 · d"], "#b98900")
s += f'<path d="M106 80 L156 45 M106 100 L156 135" stroke="{K}" stroke-width="2" stroke-linecap="round"/>'
s += t(300, 60, "count → 2") + t(300, 150, "count → 2")
s += f'<path d="M256 55 h40 M256 145 h40" stroke="{K}" stroke-width="2"/>'
s += caixa(410, 70, ["2008 · 2", "2010 · 2"], P)
s += f'<path d="M380 60 L408 80 M380 140 L408 120" stroke="{K}" stroke-width="2" stroke-linecap="round"/>'
s += t(110, 190, "1. dividir", R, 16, "middle") + t(330, 190, "2. aplicar", R, 16, "middle") + t(456, 190, "3. combinar", R, 16, "middle")
files["groupby"] = svg("0 0 520 200", 490, s)

# 7. média x mediana
s = f'<path d="M30 170 H380" stroke="{K}" stroke-width="2"/>'
for i, v in enumerate([30, 30, 30, 30, 30, 90]):
    x, h = 40 + i * 56, v * 1.4
    c, fill = (R, "#fef2f2") if v == 90 else (B, "#eef4ff")
    s += f'<rect x="{x}" y="{170 - h}" width="38" height="{h}" rx="4" fill="{fill}" stroke="{c}" stroke-width="2.5"/>'
    s += t(x + 19, 165 - h, f"{v}k", c, 15, "middle")
s += f'<path d="M30 114 H380" stroke="{G}" stroke-width="2.5" stroke-dasharray="7 5"/>' + t(386, 118, "média 40k", G)
s += f'<path d="M30 128 H380" stroke="{P}" stroke-width="2.5"/>' + t(386, 140, "mediana 30k", P)
s += t(250, 196, "o diretor puxa a média para cima; a mediana nem liga", R, 15, "middle")
files["media-mediana"] = svg("0 0 520 205", 470, s)

# 8. barras x histograma
s = f'<path d="M20 150 H230 M20 150 V20" stroke="{K}" stroke-width="2"/>'
for i, (lab, h) in enumerate([("SP", 100), ("RJ", 60), ("MG", 80)]):
    x = 40 + i * 65
    s += f'<rect x="{x}" y="{150 - h}" width="40" height="{h}" rx="3" fill="#eef4ff" stroke="{B}" stroke-width="2.5"/>' + t(x + 20, 170, lab, K, 15, "middle")
s += t(125, 195, "barras: categorias, com espaço", B, 16, "middle")
s += f'<path d="M290 150 H500 M290 150 V20" stroke="{K}" stroke-width="2"/>'
for i, h in enumerate([15, 40, 85, 110, 75, 35, 12]):
    s += f'<rect x="{300 + i * 28}" y="{150 - h}" width="28" height="{h}" fill="#f0fdf4" stroke="{G}" stroke-width="2"/>'
s += t(395, 170, "altura (faixas)", K, 14, "middle") + t(395, 195, "histograma: faixas grudadas", G, 16, "middle")
files["barras-vs-hist"] = svg("0 0 520 205", 490, s)

# 9. correlação
random.seed(4)
def nuvem(ox, slope, lab, c, val):
    r = f'<rect x="{ox}" y="20" width="150" height="130" rx="8" fill="#fff" stroke="#c3c9d4" stroke-width="1.5"/>'
    for _ in range(22):
        x = random.uniform(12, 138)
        if slope:
            y = 85 - slope * (x - 75) * 0.75 + random.uniform(-14, 14)
        else:
            y = random.uniform(30, 140)
        r += f'<circle cx="{ox + x:.0f}" cy="{max(28, min(142, y)):.0f}" r="4" fill="{c}" fill-opacity=".7"/>'
    return r + t(ox + 75, 172, lab, c, 16, "middle") + t(ox + 75, 194, val, K, 15, "middle")
files["correlacao"] = svg("0 0 520 205", 490, nuvem(10, 1, "positiva", G, "≈ +0.9") + nuvem(185, -1, "negativa", R, "≈ −0.9") + nuvem(360, 0, "nenhuma", B, "≈ 0"))

# 10. loc x iloc
s = t(195, 22, "0", R, 15, "middle") + t(305, 22, "1", R, 15, "middle")
s += t(195, 42, "flower", G, 16, "middle") + t(305, 42, "insect", G, 16, "middle")
for i, lab in enumerate(["state 1", "state 2", "state 3"]):
    y = 50 + i * 34
    s += t(30, y + 22, lab, G) + t(118, y + 22, i, R)
    s += f'<rect x="140" y="{y}" width="110" height="34" fill="#fff" stroke="#c3c9d4" stroke-width="1.5"/>'
    s += f'<rect x="250" y="{y}" width="110" height="34" fill="#fff" stroke="#c3c9d4" stroke-width="1.5"/>'
s += f'<rect x="250" y="118" width="110" height="34" fill="{Y}" fill-opacity=".35" stroke="{Y}" stroke-width="2.5"/>'
s += t(380, 100, '.loc["state 3", "insect"]', G) + t(380, 128, ".iloc[2, 1]", R) + t(380, 156, "mesma célula!", K, 15)
s += t(30, 190, "verde = rótulo (loc)", G, 15) + t(220, 190, "vermelho = posição (iloc)", R, 15)
files["loc-iloc"] = svg("0 0 560 200", 500, s)

# ------------------------------------------------------------ sprints 4 a 8
import math


def curva(x0, x1, base, alt, mu, sd, a=None, b=None):
    """Pontos de uma normal desenhada entre x0 e x1 (px). a..b recorta (para área)."""
    pts = []
    a = x0 if a is None else a
    b = x1 if b is None else b
    for i in range(0, 121):
        x = a + (b - a) * i / 120
        z = (x - mu) / sd
        pts.append((x, base - alt * math.exp(-z * z / 2)))
    return pts


def path(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def area(x0, x1, base, alt, mu, sd, a, b, cor, op):
    pts = curva(x0, x1, base, alt, mu, sd, a, b)
    return f'<path d="{path(pts)} L{b:.1f} {base} L{a:.1f} {base} Z" fill="{cor}" fill-opacity="{op}" stroke="none"/>'


# 11. boxplot
s = f'<path d="M30 130 H490" stroke="{K}" stroke-width="2"/>'
for v in range(0, 11):
    x = 40 + v * 44
    s += f'<path d="M{x} 126 v8" stroke="{K}" stroke-width="1.5"/>' + t(x, 150, v * 10, K, 13, "middle")
q1, med, q3 = 40 + 3 * 44, 40 + 4.2 * 44, 40 + 5.5 * 44
lo, hi = 40 + 1 * 44, 40 + 8.6 * 44
s += f'<path d="M{lo} 80 H{q1} M{q3} 80 H{hi} M{lo} 66 v28 M{hi} 66 v28" stroke="{B}" stroke-width="2.5" stroke-linecap="round"/>'
s += f'<rect x="{q1}" y="55" width="{q3 - q1}" height="50" rx="4" fill="#eef4ff" stroke="{B}" stroke-width="2.5"/>'
s += f'<path d="M{med} 55 v50" stroke="{P}" stroke-width="3.5"/>'
s += f'<circle cx="{40 + 9.8 * 44}" cy="80" r="6" fill="none" stroke="{R}" stroke-width="2.5"/>'
s += t(q1, 48, "Q1", B, 16, "middle") + t(med, 48, "mediana", P, 16, "middle") + t(q3, 48, "Q3", B, 16, "middle")
s += t(40 + 9.8 * 44, 66, "outlier", R, 15, "middle")
s += f'<path d="M{q1} 22 H{q3}" stroke="{G}" stroke-width="2"/><path d="M{q1} 16 v12 M{q3} 16 v12" stroke="{G}" stroke-width="2"/>'
s += t((q1 + q3) / 2, 14, "IQR = Q3 − Q1 (50% do meio)", G, 15, "middle")
s += t(250, 178, "bigodes vão até o último ponto dentro de 1,5 × IQR; o que passa disso é outlier", K, 14, "middle")
files["boxplot-quartis"] = svg("0 0 520 190", 490, s)

# 12. sino com 68/95/99,7
mu, sd, base, alt = 260, 62, 150, 120
s = ""
for k, cor, op in [(3, B, .12), (2, B, .22), (1, B, .38)]:
    s += area(20, 500, base, alt, mu, sd, mu - k * sd, mu + k * sd, cor, op)
s += f'<path d="{path(curva(40, 480, base, alt, mu, sd))}" fill="none" stroke="{K}" stroke-width="2.5"/>'
s += f'<path d="M30 {base} H490" stroke="{K}" stroke-width="2"/>'
for k in range(-3, 4):
    x = mu + k * sd
    lab = "μ" if k == 0 else f"{'+' if k > 0 else '−'}{abs(k)}σ"
    s += f'<path d="M{x} {base} v6" stroke="{K}" stroke-width="1.5"/>' + t(x, base + 22, lab, P if k == 0 else K, 15, "middle")
s += t(mu - 0.5 * sd, 120, "34%", "#fff", 15, "middle") + t(mu + 0.5 * sd, 120, "34%", "#fff", 15, "middle")
s += t(mu - 1.5 * sd, 140, "13,5%", B, 13, "middle") + t(mu + 1.5 * sd, 140, "13,5%", B, 13, "middle")
s += t(mu + 2.6 * sd, 118, "2,35%", R, 13, "middle") + t(mu - 2.6 * sd, 118, "2,35%", R, 13, "middle")
s += t(20, 24, "±1σ → 68%", P, 15) + t(20, 44, "±2σ → 95%", B, 15) + t(20, 64, "±3σ → 99,7%", R, 15)
s += t(260, 196, "quase tudo cabe em 3 desvios padrão para cada lado da média", R, 15, "middle")
files["sino-tres-sigmas"] = svg("0 0 520 205", 480, s)

# 13. eventos: interseção, exclusivos, independentes
s = (f'<circle cx="70" cy="80" r="42" fill="{B}" fill-opacity=".15" stroke="{B}" stroke-width="2.5"/>'
     f'<circle cx="120" cy="80" r="42" fill="{R}" fill-opacity=".15" stroke="{R}" stroke-width="2.5"/>'
     f'<path d="M95 46 A42 42 0 0 1 95 114 A42 42 0 0 1 95 46 Z" fill="{P}" fill-opacity=".45"/>')
s += t(50, 84, "A", B, 18, "middle") + t(140, 84, "B", R, 18, "middle")
s += t(95, 150, "interseção A ∩ B", P, 16, "middle") + t(95, 172, "os dois acontecem", K, 14, "middle")
s += (f'<circle cx="230" cy="80" r="36" fill="{B}" fill-opacity=".15" stroke="{B}" stroke-width="2.5"/>'
      f'<circle cx="320" cy="80" r="36" fill="{R}" fill-opacity=".15" stroke="{R}" stroke-width="2.5"/>')
s += t(230, 86, "cara", B, 16, "middle") + t(320, 86, "coroa", R, 16, "middle")
s += t(275, 150, "mutuamente exclusivos", G, 16, "middle") + t(275, 172, "P(A ∩ B) = 0", K, 14, "middle")
s += (f'<circle cx="410" cy="78" r="22" fill="#fffbea" stroke="{Y}" stroke-width="2.5"/>'
      f'<rect x="448" y="58" width="40" height="40" rx="8" fill="#fff" stroke="{B}" stroke-width="2.5"/>'
      f'<circle cx="460" cy="70" r="3" fill="{R}"/><circle cx="476" cy="86" r="3" fill="{R}"/>')
s += t(410, 84, "$", "#b98900", 18, "middle") + t(445, 150, "independentes", B, 16, "middle")
s += t(445, 172, "P(A ∩ B) = P(A) · P(B)", K, 14, "middle")
s += t(260, 22, "moeda e dado: um não muda a chance do outro", K, 13, "start")
files["venn-eventos"] = svg("0 0 520 185", 490, s)

# 14. cdf e ppf
mu, sd, base, alt = 260, 70, 150, 115
xq = mu + 0.9 * sd
s = area(30, 490, base, alt, mu, sd, 40, xq, G, .3) + area(30, 490, base, alt, mu, sd, xq, 480, R, .2)
s += f'<path d="{path(curva(40, 480, base, alt, mu, sd))}" fill="none" stroke="{K}" stroke-width="2.5"/>'
s += f'<path d="M30 {base} H490" stroke="{K}" stroke-width="2"/><path d="M{xq} {base} V30" stroke="{P}" stroke-width="2.5" stroke-dasharray="6 5"/>'
s += t(xq, base + 22, "x", P, 17, "middle")
s += t(200, 120, "cdf(x)", G, 18, "middle") + t(200, 140, "área à esquerda", G, 14, "middle")
s += t(xq + 95, 80, "1 − cdf(x)", R, 16, "middle") + t(xq + 95, 98, "área à direita", R, 14, "middle")
s += f'<path d="M{xq + 60} 104 L{xq + 30} 136" stroke="{R}" stroke-width="1.5"/>'
s += t(20, 24, "cdf: dou o x, recebo a área", G, 15) + t(300, 24, "ppf: dou a área, recebo o x", P, 15)
s += t(260, 196, "o \"1 −\" vai por fora da cdf (área à direita) e por dentro da ppf: ppf(1 − 0,05)", K, 13.5, "middle")
files["cdf-ppf"] = svg("0 0 520 205", 490, s)

# 15. caudas bicaudal x unicaudal
def mini_sino(ox, caudas):
    mu, sd, base, alt = ox + 115, 40, 140, 100
    r = ""
    z = 1.96 if caudas == 2 else 1.645
    if caudas == 2:
        r += area(ox, ox + 230, base, alt, mu, sd, ox + 5, mu - z * sd, R, .55) + area(ox, ox + 230, base, alt, mu, sd, mu + z * sd, ox + 225, R, .55)
        r += t(mu - 2.6 * sd, 118, "2,5%", R, 14, "middle") + t(mu + 2.6 * sd, 118, "2,5%", R, 14, "middle")
    else:
        r += area(ox, ox + 230, base, alt, mu, sd, mu + z * sd, ox + 225, R, .55)
        r += t(mu + 2.5 * sd, 112, "5%", R, 15, "middle")
    r += f'<path d="{path(curva(ox + 5, ox + 225, base, alt, mu, sd))}" fill="none" stroke="{K}" stroke-width="2.5"/>'
    r += f'<path d="M{ox} {base} H{ox + 230}" stroke="{K}" stroke-width="2"/>'
    return r
s = mini_sino(10, 2) + mini_sino(275, 1)
s += t(125, 168, "bicaudal: \"é diferente?\"", B, 16, "middle") + t(390, 168, "unicaudal: \"é maior?\"", B, 16, "middle")
s += t(125, 190, "α = 5% dividido nas duas pontas", K, 14, "middle") + t(390, 190, "α = 5% inteiro numa ponta só", K, 14, "middle")
s += t(260, 22, "vermelho = região onde rejeito H0", R, 15, "middle")
files["caudas-hipotese"] = svg("0 0 520 200", 490, s)

# 16. joins
def join(ox, titulo, esq, dir_, meio):
    a = f'<circle cx="{ox + 55}" cy="80" r="40" fill="{B}" fill-opacity="{.35 if esq else 0}" stroke="{B}" stroke-width="2.5"/>'
    b = f'<circle cx="{ox + 105}" cy="80" r="40" fill="{R}" fill-opacity="{.35 if dir_ else 0}" stroke="{R}" stroke-width="2.5"/>'
    m = f'<path d="M{ox + 80} 48.8 A40 40 0 0 1 {ox + 80} 111.2 A40 40 0 0 1 {ox + 80} 48.8 Z" fill="{P}" fill-opacity="{.55 if meio else 0}"/>'
    return a + b + m + t(ox + 80, 145, titulo, K, 17, "middle") + t(ox + 40, 85, "A", B, 16, "middle") + t(ox + 120, 85, "B", R, 16, "middle")
s = join(5, "INNER JOIN", False, False, True) + join(180, "LEFT JOIN", True, False, True) + join(355, "RIGHT JOIN", False, True, True)
s += t(85, 168, "só o que casa", P, 14, "middle") + t(260, 168, "tudo de A + o que casa", B, 14, "middle") + t(435, 168, "tudo de B + o que casa", R, 14, "middle")
s += t(260, 22, "A = tabela do FROM (esquerda), B = tabela do JOIN (direita)", K, 14, "middle")
s += t(260, 192, "linha de A sem par em B volta com NULL nas colunas de B", G, 14, "middle")
files["joins-venn"] = svg("0 0 520 200", 490, s)

# 17. ordem de execução SQL (escada subindo)
passos = ["FROM", "WHERE", "GROUP BY", "HAVING", "SELECT", "ORDER BY", "LIMIT"]
s = ""
for i, p_ in enumerate(passos):
    x, y = 14 + i * 70, 170 - i * 20
    cor = R if p_ == "SELECT" else B
    s += f'<rect x="{x}" y="{y - 26}" width="66" height="30" rx="7" fill="{"#fef2f2" if p_ == "SELECT" else "#eef4ff"}" stroke="{cor}" stroke-width="2.5"/>'
    s += t(x + 33, y - 6, p_, cor, 12 if len(p_) > 6 else 13.5, "middle") + t(x + 33, y + 18, i + 1, K, 14, "middle")
s += t(20, 28, "a gente escreve SELECT primeiro,", K, 15) + t(20, 48, "mas o banco executa nesta ordem", K, 15)
s += t(330, 196, "por isso o apelido do SELECT não vale no WHERE", R, 14, "middle")
files["ordem-execucao-sql"] = svg("0 0 520 205", 490, s)

# 18. GROUP BY x OVER
def tab(ox, oy, linhas, cols, cores):
    r = ""
    for i, ln in enumerate(linhas):
        for j, v in enumerate(ln):
            r += f'<rect x="{ox + j * 52}" y="{oy + i * 26}" width="52" height="26" fill="{cores[i] if j == 0 else "#fff"}" stroke="#c3c9d4" stroke-width="1.5"/>'
            r += t(ox + j * 52 + 26, oy + i * 26 + 18, v, K, 14, "middle")
    return r
cA, cB = "#eef4ff", "#fff7ed"
s = tab(10, 40, [["A", "10"], ["A", "20"], ["B", "5"], ["B", "15"]], 2, [cA, cA, cB, cB])
s += f'<path d="M120 92 h36" stroke="{K}" stroke-width="2.5"/><path d="M150 86 l8 6 -8 6" fill="none" stroke="{K}" stroke-width="2.5"/>'
s += tab(166, 66, [["A", "30"], ["B", "20"]], 2, [cA, cB])
s += t(140, 22, "GROUP BY: as linhas se juntam", R, 15, "middle") + t(140, 170, "4 linhas viram 2", R, 14, "middle")
s += f'<path d="M282 20 V180" stroke="#c3c9d4" stroke-width="2" stroke-dasharray="5 6"/>'
s += tab(300, 40, [["A", "10", "30"], ["A", "20", "30"], ["B", "5", "20"], ["B", "15", "20"]], 3, [cA, cA, cB, cB])
s += f'<rect x="404" y="40" width="52" height="104" fill="none" stroke="{G}" stroke-width="3" rx="3"/>'
s += t(390, 22, "OVER: as linhas ficam", G, 15, "middle") + t(390, 170, "SUM(...) OVER (PARTITION BY grupo)", G, 13, "middle")
s += t(260, 196, "a janela calcula por grupo e devolve o resultado em cada linha", K, 14, "middle")
files["group-vs-over"] = svg("0 0 520 205", 490, s)

# 19. escada do lucro (descendo)
degraus = [("Receita", "1.000.000", B), ("Lucro bruto", "700.000", G), ("Lucro operacional", "500.000", "#b98900"), ("Lucro líquido", "440.000", P)]
gastos = ["− custo primário", "− custos operacionais", "− impostos e juros"]
s = ""
for i, (nome, v, c) in enumerate(degraus):
    x, y, w = 10 + i * 30, 20 + i * 44, 200 - i * 30
    s += f'<rect x="{x}" y="{y}" width="{w + 60}" height="36" rx="6" fill="#fff" stroke="{c}" stroke-width="2.5"/>'
    s += t(x + 10, y + 24, nome, c, 16) + t(x + w + 52, y + 24, v, K, 15, "end")
    if i < 3:
        s += t(x + w + 80, y + 46, gastos[i], R, 15)
        s += f'<path d="M{x + w + 66} {y + 36} q8 4 0 8" fill="none" stroke="{R}" stroke-width="2"/>'
s += t(260, 218, "cada degrau tira um tipo de gasto; a margem divide sempre pela receita do topo", K, 13.5, "middle")
files["escada-lucro"] = svg("0 0 520 228", 490, s)

# 20. funil
etapas = [("Página principal", 10000), ("Produto", 8000), ("Carrinho", 3000), ("Checkout", 1000), ("Pagou", 100)]
s = ""
for i, (nome, n) in enumerate(etapas):
    w = max(30, 300 * n / 10000)
    x, y = 170 - w / 2, 16 + i * 36
    s += f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="#eef4ff" stroke="{B}" stroke-width="2.5"/>'
    s += t(330, y + 20, f"{nome}: {n:,}".replace(",", "."), K, 15)
    if i:
        perc = n / etapas[i - 1][1] * 100
        s += t(505, y + 20, f"{perc:.0f}%", R if perc < 20 else G, 15, "end")
s += t(12, 205, "% = quantos passaram da etapa anterior para esta; o vermelho é onde mais vaza", R, 13.5)
files["funil"] = svg("0 0 520 212", 480, s)

# 21. coortes em escada
meses = ["jan", "fev", "mar", "abr"]
vals = [[100, 40, 30, 25], [None, 120, 45, 33], [None, None, 90, 30], [None, None, None, 110]]
heat = ["#2b0a3d", "#7a1f5c", "#c8354a", "#f29e6d", "#fbe3c8"]
s = ""
for j, m in enumerate(meses):
    s += t(150 + j * 64, 30, m, B, 15, "middle")
for i, m in enumerate(meses):
    s += t(80, 62 + i * 34, f"coorte {m}", P, 14, "end")
    for j in range(4):
        v = vals[i][j]
        x, y = 118 + j * 64, 40 + i * 34
        if v is None:
            s += f'<rect x="{x}" y="{y}" width="64" height="34" fill="#fff" stroke="#e2e6ee" stroke-width="1" stroke-dasharray="3 4"/>'
            continue
        c = heat[0] if v >= 100 else heat[1] if v >= 40 else heat[2] if v >= 30 else heat[3]
        s += f'<rect x="{x}" y="{y}" width="64" height="34" fill="{c}" stroke="#fff" stroke-width="1.5"/>'
        s += t(x + 32, y + 23, v, "#fff" if v >= 30 else K, 15, "middle")
s += t(380, 70, "linha = a vida", P, 15) + t(380, 90, "de uma coorte", P, 15)
s += t(380, 130, "coluna = mês", B, 15) + t(380, 150, "do calendário", B, 15)
s += t(380, 186, "vazio = coorte", K, 14) + t(380, 204, "ainda não existia", K, 14)
files["coorte-escada"] = svg("0 0 520 212", 480, s)

# 22. balança LTV x CAC
s = f'<path d="M200 40 V180 M150 180 H250" stroke="{K}" stroke-width="3" stroke-linecap="round"/>'
s += f'<path d="M80 60 L320 30" stroke="{K}" stroke-width="3" stroke-linecap="round"/><circle cx="200" cy="45" r="5" fill="{K}"/>'
s += f'<path d="M80 60 L50 110 M80 60 L110 110 M320 30 L290 80 M320 30 L350 80" stroke="{K}" stroke-width="1.5"/>'
s += f'<path d="M40 110 H120 q-6 18 -40 18 q-34 0 -40 -18 Z" fill="#f0fdf4" stroke="{G}" stroke-width="2.5"/>'
s += f'<path d="M280 80 H360 q-6 18 -40 18 q-34 0 -40 -18 Z" fill="#fef2f2" stroke="{R}" stroke-width="2.5"/>'
s += t(80, 104, "LTV", G, 18, "middle") + t(320, 74, "CAC", R, 18, "middle")
s += t(80, 150, "o que o cliente", G, 14, "middle") + t(80, 168, "deixa de lucro", G, 14, "middle")
s += t(320, 122, "o que custou", R, 14, "middle") + t(320, 140, "trazer ele", R, 14, "middle")
s += t(390, 40, "LTV / CAC", P, 17) + t(390, 62, "> 1: o cliente", G, 15) + t(390, 80, "se paga", G, 15)
s += t(390, 110, "< 1: cada cliente", R, 15) + t(390, 128, "dá prejuízo", R, 15)
files["ltv-cac-balanca"] = svg("0 0 520 190", 480, s)

for name, content in files.items():
    (OUT / f"{name}.svg").write_text(content, encoding="utf-8")
print(", ".join(sorted(files)))
