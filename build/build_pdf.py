"""Monta o Guia de Estudos em PDF a partir de content/*.md e data/*.yaml.

Uso:  python build/build_pdf.py
Saída: Guia_de_Estudos_DA.pdf na raiz do projeto.

Passos:
1. Lê os capítulos (frontmatter + markdown) e os dicionários.
2. Gera um HTML único (capa, sumário, capítulos, fórmulas, siglas).
3. Imprime em PDF com o Chrome headless.
4. Pós-processa com PyMuPDF: números de página no sumário, botão
   "Sumário" em todas as páginas, marcadores (outline) e rodapé.
"""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import markdown
import pymupdf
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DATA = ROOT / "data"
OUT_PDF = ROOT / "Guia_de_Estudos_DA.pdf"
CSS = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
import didatico  # noqa: E402  notas à mão, ícones e desenhos (só nos capítulos)
CSS += didatico.CSS

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
SEGOE = r"C:\Windows\Fonts\segoeui.ttf"
SEGOE_B = r"C:\Windows\Fonts\segoeuib.ttf"

CARD_TITLES = {
    "def": "Definição",
    "regra": "Regra de ouro",
    "erro": "Armadilha",
    "dica": "Dica",
    "ex": "Exemplo",
    "comp": "Comparação",
    "ver": "Ver também",
    "novo": "Complemento",
}

MD_EXT = ["fenced_code", "tables", "sane_lists", "attr_list", "md_in_html"]


# ---------------------------------------------------------------- leitura
def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def cap_key(cap: str):
    return tuple(int(p) for p in cap.split("."))


def read_chapters():
    chapters = []
    for f in CONTENT.rglob("*.md"):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            print(f"! sem frontmatter: {f}", file=sys.stderr)
            continue
        meta = yaml.safe_load(m.group(1))
        meta["body"] = m.group(2)
        meta["cap"] = str(meta["cap"])
        meta["id"] = "c" + meta["cap"].replace(".", "-")
        chapters.append(meta)
    chapters.sort(key=lambda c: cap_key(c["cap"]))
    return chapters


# ------------------------------------------------------- markdown -> html
def md(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXT, output_format="html5")


def render_cards(body: str) -> str:
    """Troca blocos '> [!tipo] Título' por <div class="card tipo">."""
    out, lines, i = [], body.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^> \[!(\w+)\]\s*(.*)$", lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        kind, title = m.group(1), m.group(2).strip() or CARD_TITLES.get(m.group(1), "")
        inner = []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            inner.append(re.sub(r"^> ?", "", lines[i]))
            i += 1
        if kind == "corrigido":
            out.append(didatico.corrigido_html(m.group(2).strip(), md(chr(10).join(inner))))
            continue
        out.append(
            f'\n<div class="card {kind}"><div class="card-t">{didatico.icon(kind)}{html.escape(title)}</div>'
            f"{md(chr(10).join(inner))}</div>\n"
        )
    return "\n".join(out)


def render_fluxo(body: str) -> str:
    def repl(m):
        steps = [s.strip() for s in m.group(1).strip().split("→")]
        chips = '<span class="arrow">→</span>'.join(
            f'<span class="step">{html.escape(s)}</span>' for s in steps
        )
        return f'\n<div class="fluxo">{chips}</div>\n'

    return re.sub(r"```fluxo\n(.*?)\n```", repl, body, flags=re.S)


def render_formula_blocks(body: str) -> str:
    """```formula  Nome = numerador / denominador  -> caixa escura com fração."""
    def repl(m):
        rows = []
        for line in m.group(1).strip().split("\n"):
            rows.append(formula_html(line.strip()))
        return '\n<div class="formula-box">' + "".join(rows) + "</div>\n"

    return re.sub(r"```formula\n(.*?)\n```", repl, body, flags=re.S)


def formula_html(expr: str) -> str:
    """'Lado = num // den' vira fração; sem '//' fica em linha."""
    if "=" in expr:
        left, right = expr.split("=", 1)
    else:
        left, right = "", expr
    right = right.strip()
    if "//" in right:
        num, den = right.split("//", 1)
        rhs = (
            f'<span class="frac"><span class="num">{html.escape(num.strip())}</span>'
            f'<span class="den">{html.escape(den.strip())}</span></span>'
        )
    else:
        rhs = f'<span class="inline">{html.escape(right)}</span>'
    lhs = f'<span class="lhs">{html.escape(left.strip())}</span><span class="eq">=</span>' if left else ""
    return f'<div class="formula">{lhs}{rhs}</div>'


def chapter_html(ch, toc):
    body = render_formula_blocks(render_fluxo(didatico.render_desenhos(ch["body"])))
    body = render_cards(body)
    h = md(body)
    sections = []

    def h2(m):
        n = len(sections) + 1
        sid = f'{ch["id"]}-s{n}'
        title = re.sub(r"<.*?>", "", m.group(1))
        sections.append((title, sid))
        return f'<h2 id="{sid}">{m.group(1)}</h2>'

    h = re.sub(r"<h2>(.*?)</h2>", h2, h)
    toc.append((2, f'{ch["cap"]}  {ch["title"]}', ch["id"]))
    for title, sid in sections:
        toc.append((3, html.unescape(title), sid))
    tag = f'Sprint {ch["sprint"]} · {html.escape(ch["sprint_title"])}'
    sa = f'<a id="{ch["sprint_anchor"]}"></a>' if ch.get("sprint_anchor") else ""
    return (
        f'<section class="chapter" id="{ch["id"]}">{sa}'
        f'<div class="tag">{tag}</div>'
        f'<h1><span class="capnum">{ch["cap"]}</span>{html.escape(ch["title"])}{didatico.chapter_doodle(ch["cap"])}</h1>'
        f"{h}</section>"
    )


# ------------------------------------------------------------ dicionários
def letter_of(term: str) -> str:
    t = unicodedata.normalize("NFKD", term).encode("ascii", "ignore").decode().upper()
    t = re.sub(r"^[^A-Z0-9]+", "", t)
    return t[:1] if t and t[0].isalpha() else "#"


def sort_key(term: str):
    t = unicodedata.normalize("NFKD", term).encode("ascii", "ignore").decode().lower()
    return re.sub(r"^[^a-z0-9]+", "", t)


def chapter_link(ref: str, chapters_by_cap) -> str:
    ch = chapters_by_cap.get(str(ref))
    if not ch:
        return html.escape(str(ref))
    return f'<a href="#{ch["id"]}">{ch["cap"]}</a>'


def formulas_html(chapters_by_cap, toc):
    path = DATA / "formulas.yaml"
    items = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else []
    items = sorted(items or [], key=lambda x: sort_key(x["nome"]))
    toc.append((1, "Dicionário de fórmulas", "formulas"))
    parts = ['<section class="dict" id="formulas"><div class="tag">Consulta rápida</div>'
             "<h1>Dicionário de fórmulas</h1>"
             '<p class="lead">Em ordem alfabética. O número no fim de cada fórmula leva ao capítulo onde ela é explicada.</p>']
    current = None
    for it in items:
        L = letter_of(it["nome"])
        if L != current:
            current = L
            lid = f"f-{L}"
            parts.append(f'<h2 class="letter" id="{lid}">{L}</h2>')
            toc.append((3, L, lid))
        refs = ", ".join(chapter_link(r, chapters_by_cap) for r in it.get("caps", []))
        exprs = "".join(formula_html(e) for e in it["formula"].strip().split("\n"))
        leg = ""
        if it.get("legenda"):
            leg = '<div class="legenda">' + md(it["legenda"]) + "</div>"
        parts.append(
            f'<div class="fitem"><div class="fhead"><span class="fname">{html.escape(it["nome"])}</span>'
            f'<span class="fref">{refs}</span></div>'
            f'<div class="formula-box small">{exprs}</div>{leg}</div>'
        )
    parts.append("</section>")
    return "".join(parts)


def siglas_html(chapters_by_cap, toc):
    path = DATA / "siglas.yaml"
    items = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else []
    items = sorted(items or [], key=lambda x: sort_key(x["sigla"]))
    toc.append((1, "Dicionário de siglas", "siglas"))
    parts = ['<section class="dict" id="siglas"><div class="tag">Consulta rápida</div>'
             "<h1>Dicionário de siglas</h1>"
             '<p class="lead">Só o significado. A explicação completa está no capítulo indicado.</p>']
    current = None
    for it in items:
        L = letter_of(it["sigla"])
        if L != current:
            if current is not None:
                parts.append("</table>")
            current = L
            lid = f"s-{L}"
            parts.append(f'<h2 class="letter" id="{lid}">{L}</h2><table class="siglas">')
            toc.append((3, L, lid))
        refs = ", ".join(chapter_link(r, chapters_by_cap) for r in it.get("caps", []))
        parts.append(
            f'<tr><td class="sg">{html.escape(it["sigla"])}</td>'
            f'<td><b>{html.escape(it["significado"])}</b>'
            f'{"<br><span class=desc>" + html.escape(it["desc"]) + "</span>" if it.get("desc") else ""}</td>'
            f'<td class="fref">{refs}</td></tr>'
        )
    if current is not None:
        parts.append("</table>")
    parts.append("</section>")
    return "".join(parts)


# ------------------------------------------------------------------ html
def build_html():
    chapters = read_chapters()
    by_cap = {c["cap"]: c for c in chapters}
    toc: list[tuple[int, str, str]] = []
    body = []
    last_sprint = None
    for ch in chapters:
        if ch["sprint"] != last_sprint:
            last_sprint = ch["sprint"]
            toc.append((1, f'Sprint {ch["sprint"]} · {ch["sprint_title"]}', f's{ch["sprint"]}'))
            ch = dict(ch, sprint_anchor=f's{ch["sprint"]}')
        body.append(chapter_html(ch, toc))
    body.append(formulas_html(by_cap, toc))
    body.append(siglas_html(by_cap, toc))

    # sumário: sprint e capítulo sempre; seções (nível 3) dos capítulos também,
    # letras dos dicionários não (ficam só nos marcadores do PDF)
    toc_items = []
    for lvl, title, anchor in toc:
        if lvl == 3 and (anchor.startswith("f-") or anchor.startswith("s-")):
            continue
        toc_items.append(
            f'<a class="toc l{lvl}" href="#{anchor}" data-anchor="{anchor}">'
            f'<span class="t">{html.escape(title)}</span><span class="dots"></span>'
            f'<span class="pg"></span></a>'
        )
    cover = (
        '<section class="cover"><div class="tag">TripleTen · Analista de Dados</div>'
        "<h1>Guia de Estudos</h1>"
        '<p class="sub">Python, pandas, estatística, SQL e métricas de negócio.<br>'
        "Reorganizado a partir das anotações dos sprints, com dicionário de fórmulas e de siglas no fim.</p>"
        '<p class="how">Clique em qualquer item do sumário para ir ao assunto. '
        'Em todas as páginas, o botão <b>Sumário</b> no canto de cima leva de volta.</p></section>'
    )
    toc_html = '<section class="tocpage" id="sumario"><h1>Sumário</h1>' + "".join(toc_items) + "</section>"
    doc = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        f"<title>Guia de Estudos · Análise de Dados</title><style>{CSS}</style></head><body>"
        + cover + toc_html + "".join(body) + "</body></html>"
    )
    return doc, toc


# ------------------------------------------------------------------- pdf
def print_pdf(html_path: Path, pdf_path: Path):
    chrome = next((c for c in CHROME_CANDIDATES if Path(c).exists()), None)
    if not chrome:
        sys.exit("Chrome/Edge não encontrado")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--user-data-dir={prof}", f"--print-to-pdf={pdf_path}",
             html_path.as_uri()],
            check=True, capture_output=True, timeout=180,
        )


def postprocess(pdf_path: Path, toc, out_path: Path):
    doc = pymupdf.open(pdf_path)

    # página de cada âncora, a partir dos links do sumário
    # os links do sumário aparecem na mesma ordem de toc (sem as letras)
    toc_no_letters = [t for t in toc if not (t[0] == 3 and t[2][:2] in ("f-", "s-"))]
    toc_pages = []
    anchor_page = {}
    found = 0
    for pno in range(1, len(doc)):
        n = sum(1 for l in doc[pno].get_links() if l.get("kind") in (pymupdf.LINK_GOTO, pymupdf.LINK_NAMED))
        if n:
            toc_pages.append(pno)
            found += n
        if found >= len(toc_no_letters):
            break
    if found != len(toc_no_letters):
        print(f"! sumário: {found} links para {len(toc_no_letters)} itens", file=sys.stderr)
    seq = []
    for pno in toc_pages:
        ls = sorted(
            (l for l in doc[pno].get_links() if l.get("kind") in (pymupdf.LINK_GOTO, pymupdf.LINK_NAMED)),
            key=lambda l: (round(l["from"].y0), l["from"].x0),
        )
        seq.extend((pno, l) for l in ls)
    for (pno, link), (lvl, title, anchor) in zip(seq, toc_no_letters):
        anchor_page[anchor] = link["page"]
    first_toc = toc_pages[0] if toc_pages else 1

    # números de página no sumário
    for (pno, link), (lvl, title, anchor) in zip(seq, toc_no_letters):
        page = doc[pno]
        r = link["from"]
        num = str(link["page"] + 1)
        fs = 10 if lvl < 3 else 8.5
        font = pymupdf.Font(fontfile=SEGOE)
        w = font.text_length(num, fontsize=fs)
        y = r.y0 + (r.height + fs * 0.7) / 2
        page.insert_text((r.x1 - 6 - w, y), num, fontsize=fs, fontname="segoe",
                         fontfile=SEGOE, color=(0.25, 0.28, 0.35))

    # letras dos dicionários: acha a página pelo texto
    def find_letter_pages(sec_anchor, prefix):
        start = anchor_page.get(sec_anchor)
        if start is None:
            return
        for lvl, title, anchor in toc:
            if anchor.startswith(prefix):
                for p in range(start, len(doc)):
                    if any(b for b in doc[p].get_text("dict")["blocks"]
                           for ln in b.get("lines", []) for sp in ln["spans"]
                           if sp["text"].strip() == title and sp["size"] > 15):
                        anchor_page[anchor] = p
                        start = p
                        break

    find_letter_pages("formulas", "f-")
    find_letter_pages("siglas", "s-")

    # botão Sumário + rodapé
    for pno in range(len(doc)):
        page = doc[pno]
        W, H = page.rect.width, page.rect.height
        if pno > first_toc + len(toc_pages) - 1:
            btn = pymupdf.Rect(W - 92, 12, W - 18, 32)
            shape = page.new_shape()
            shape.draw_rect(btn, radius=0.5)
            shape.finish(color=(0.15, 0.39, 0.92), fill=(0.15, 0.39, 0.92))
            shape.commit()
            page.insert_textbox(pymupdf.Rect(btn.x0, btn.y0 + 3.5, btn.x1, btn.y1),
                                "↑  Sumário", fontsize=9, fontname="segoeb",
                                fontfile=SEGOE_B, color=(1, 1, 1),
                                align=pymupdf.TEXT_ALIGN_CENTER)
            page.insert_link({"kind": pymupdf.LINK_GOTO, "from": btn,
                              "page": first_toc, "to": pymupdf.Point(0, 0)})
        if pno > 0:
            page.insert_textbox(pymupdf.Rect(0, H - 26, W - 24, H - 10), str(pno + 1),
                                fontsize=8.5, fontname="segoe", fontfile=SEGOE,
                                color=(0.55, 0.58, 0.65), align=pymupdf.TEXT_ALIGN_RIGHT)

    # marcadores (painel lateral do leitor de PDF)
    outline = [[1, "Sumário", first_toc + 1]]
    for lvl, title, anchor in toc:
        if anchor in anchor_page:
            outline.append([lvl, title, anchor_page[anchor] + 1])
    # níveis não podem pular (1 -> 3): ajusta
    fixed, prev = [], 0
    for lvl, title, p in outline:
        lvl = min(lvl, prev + 1)
        fixed.append([lvl, title, p])
        prev = lvl
    doc.set_toc(fixed)
    doc.set_metadata({"title": "Guia de Estudos · Análise de Dados", "author": "Cauê"})
    doc.save(out_path, garbage=3, deflate=True)
    return len(doc)


def main():
    doc_html, toc = build_html()
    build_dir = ROOT / "build" / "out"
    build_dir.mkdir(parents=True, exist_ok=True)
    html_path = build_dir / "guia.html"
    html_path.write_text(doc_html, encoding="utf-8")
    raw_pdf = build_dir / "guia_raw.pdf"
    print_pdf(html_path, raw_pdf)
    n = postprocess(raw_pdf, toc, OUT_PDF)
    fixed_links = pymupdf.open(OUT_PDF)
    named_to_page_links(fixed_links)
    fixed_links.save(OUT_PDF, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    fixed_links.close()
    print(f"ok: {OUT_PDF.name} ({n} páginas)")
    copy_to_drive()


def named_to_page_links(doc):
    """O Chrome grava os links internos como destinos com nome (#c2-2).
    Vários leitores (Drive, navegadores, alguns apps de celular) não seguem
    esse tipo. Troca cada um por um link direto para página + posição."""
    for page in doc:
        named = [l for l in page.get_links()
                 if l.get("kind") == pymupdf.LINK_NAMED and l.get("page", -1) >= 0]
        for link in named:
            page.delete_link(link)
        for link in named:
            page.insert_link({"kind": pymupdf.LINK_GOTO, "from": link["from"],
                              "page": link["page"],
                              "to": link.get("to") or pymupdf.Point(0, 0), "zoom": 0})


# Cópia no Google Drive (pasta sincronizada pelo Drive para computador).
# Fica numa subpasta para não se misturar com as anotações dos capítulos.
DRIVE_DIR = Path(r"G:\My Drive\Triple Ten\Guia de Estudos")


def copy_to_drive():
    if not DRIVE_DIR.parent.exists():
        print("! Drive não encontrado; cópia não atualizada", file=sys.stderr)
        return
    DRIVE_DIR.mkdir(exist_ok=True)
    shutil.copy2(OUT_PDF, DRIVE_DIR / OUT_PDF.name)
    print(f"ok: cópia atualizada em {DRIVE_DIR}")


if __name__ == "__main__":
    main()
