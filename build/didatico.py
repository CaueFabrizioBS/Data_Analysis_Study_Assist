"""Parte "caderno" do guia: notas de correção à mão, ícones e desenhos.

Usado só nos capítulos. Dicionários e mapas ficam sem nada disso.

No markdown dos capítulos:

    > [!corrigido] Título opcional
    > No caderno: o que estava anotado
    > O certo: a correção

    ```desenho nome-do-arquivo
    legenda opcional, escrita à mão embaixo do desenho
    ```

Os desenhos ficam em build/desenhos/<nome>.svg.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).parent
DESENHOS = HERE / "desenhos"
CSS = (HERE / "didatico.css").read_text(encoding="utf-8")

# Ícones de traço simples (24x24, stroke = cor do título do card)
_I = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
ICONS = {
    "def": _I.format('<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/><path d="M9 7h6M9 11h5"/>'),
    "regra": _I.format('<path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.5 6.7 19.4l1.2-6L3.4 9.3l6-.7z"/>'),
    "erro": _I.format('<path d="M12 3 2 20h20z"/><path d="M12 10v4"/><circle cx="12" cy="17" r=".6" fill="currentColor"/>'),
    "dica": _I.format('<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>'),
    "ex": _I.format('<path d="M15 4l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/>'),
    "comp": _I.format('<path d="M12 3v18M5 21h14"/><path d="M5 7h14"/><path d="M5 7 2 14a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>'),
    "ver": _I.format('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "novo": _I.format('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>'),
}

# Rabisco ao lado do título de cada capítulo
_C = '<svg class="cap-doodle" viewBox="0 0 64 64" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{}</svg>'
CHAPTER_DOODLES = {
    "notebook": _C.format('<rect x="12" y="8" width="38" height="48" rx="4" stroke="#2b59c3"/><path d="M12 18h-4M12 30h-4M12 42h-4" stroke="#2b59c3"/><path d="M20 20h22M20 28h18M20 36h22" stroke="#e0453a"/>'),
    "caixa": _C.format('<path d="M10 22 32 12l22 10v22L32 54 10 44z" stroke="#2b59c3"/><path d="M10 22l22 10 22-10M32 32v22" stroke="#2b59c3"/><text x="25" y="27" font-size="9" fill="#e0453a" stroke="none" font-family="Letra do Caue, Ink Free">x=5</text>'),
    "aspas": _C.format('<path d="M14 18c-6 4-6 12 0 14M26 18c-6 4-6 12 0 14" stroke="#e0453a"/><path d="M30 44h26M30 52h18" stroke="#2b59c3"/><text x="32" y="36" font-size="14" fill="#2f9e44" stroke="none" font-family="Letra do Caue, Ink Free">abc</text>'),
    "lista": _C.format('<rect x="6" y="24" width="14" height="16" rx="2" stroke="#2b59c3"/><rect x="25" y="24" width="14" height="16" rx="2" stroke="#2b59c3"/><rect x="44" y="24" width="14" height="16" rx="2" stroke="#2b59c3"/><path d="M4 20c-2 4-2 20 0 24M60 20c2 4 2 20 0 24" stroke="#e0453a"/>'),
    "ciclo": _C.format('<path d="M48 20a18 18 0 1 0 4 16" stroke="#2b59c3"/><path d="M50 10v10H40" stroke="#e0453a"/>'),
    "bifurca": _C.format('<path d="M32 56V34M32 34 16 14M32 34l16-20" stroke="#2b59c3"/><path d="M10 18l6-4 2 7M54 18l-6-4-2 7" stroke="#e0453a"/>'),
    "chave": _C.format('<circle cx="20" cy="32" r="10" stroke="#f2b705"/><path d="M30 32h26M48 32v8M54 32v6" stroke="#f2b705"/>'),
    "engrenagem": _C.format('<circle cx="32" cy="32" r="9" stroke="#2b59c3"/><path d="M32 8v8M32 48v8M8 32h8M48 32h8M15 15l6 6M43 43l6 6M15 49l6-6M43 21l6-6" stroke="#e0453a"/>'),
    "panda": _C.format('<circle cx="32" cy="34" r="18" stroke="#1f2430"/><circle cx="18" cy="18" r="6" stroke="#1f2430" fill="#1f2430"/><circle cx="46" cy="18" r="6" stroke="#1f2430" fill="#1f2430"/><ellipse cx="25" cy="32" rx="4" ry="5" fill="#1f2430"/><ellipse cx="39" cy="32" rx="4" ry="5" fill="#1f2430"/><path d="M29 42q3 3 6 0" stroke="#1f2430"/>'),
    "vassoura": _C.format('<path d="M44 6 30 34" stroke="#b5651d"/><path d="M30 34l-14 8 4 14 22-10-4-10z" stroke="#f2b705"/><path d="M22 44l4 10M28 42l4 10" stroke="#f2b705"/>'),
    "lupa": _C.format('<circle cx="26" cy="26" r="14" stroke="#2b59c3"/><path d="M36 36l18 18" stroke="#2b59c3"/><path d="M20 26h12" stroke="#2f9e44"/>'),
    "buraco": _C.format('<rect x="8" y="10" width="48" height="44" rx="4" stroke="#2b59c3"/><path d="M8 24h48M8 38h48M24 10v44M40 10v44" stroke="#2b59c3"/><text x="27" y="35" font-size="11" fill="#e0453a" stroke="none" font-family="Letra do Caue, Ink Free">NaN</text>'),
    "funil": _C.format('<path d="M8 10h48L38 32v20l-12 6V32z" stroke="#2b59c3"/><path d="M16 18h32" stroke="#e0453a"/>'),
    "grafico": _C.format('<path d="M8 8v48h48" stroke="#1f2430"/><rect x="14" y="34" width="8" height="18" stroke="#2b59c3"/><rect x="28" y="22" width="8" height="30" stroke="#2f9e44"/><rect x="42" y="14" width="8" height="38" stroke="#e0453a"/>'),
    "calendario": _C.format('<rect x="8" y="12" width="48" height="42" rx="4" stroke="#2b59c3"/><path d="M8 24h48M20 6v10M44 6v10" stroke="#2b59c3"/><circle cx="32" cy="38" r="5" stroke="#e0453a"/>'),
    "sino": _C.format('<path d="M8 52c8 0 10-40 24-40s16 40 24 40" stroke="#2b59c3"/><path d="M8 52h48" stroke="#1f2430"/><path d="M32 12v40" stroke="#e0453a" stroke-dasharray="3 4"/>'),
    "dado": _C.format('<rect x="12" y="12" width="40" height="40" rx="8" stroke="#2b59c3"/><circle cx="22" cy="22" r="3" fill="#e0453a"/><circle cx="32" cy="32" r="3" fill="#e0453a"/><circle cx="42" cy="42" r="3" fill="#e0453a"/>'),
    "balanca": _C.format('<path d="M32 8v46M18 54h28M12 16h40" stroke="#2b59c3"/><path d="M12 16 6 32a6 6 0 0 0 12 0zM52 16l-6 16a6 6 0 0 0 12 0z" stroke="#e0453a"/>'),
    "terminal": _C.format('<rect x="6" y="10" width="52" height="44" rx="4" stroke="#1f2430"/><path d="M14 26l8 6-8 6" stroke="#2f9e44"/><path d="M26 40h14" stroke="#2f9e44"/>'),
    "banco": _C.format('<ellipse cx="32" cy="14" rx="20" ry="7" stroke="#2b59c3"/><path d="M12 14v34c0 4 9 7 20 7s20-3 20-7V14" stroke="#2b59c3"/><path d="M12 31c0 4 9 7 20 7s20-3 20-7" stroke="#2b59c3"/>'),
    "pessoas": _C.format('<circle cx="22" cy="22" r="7" stroke="#2b59c3"/><circle cx="44" cy="22" r="7" stroke="#e0453a"/><path d="M8 52c0-10 6-16 14-16s14 6 14 16M30 52c0-10 6-16 14-16s14 6 14 16" stroke="#1f2430"/>'),
    "moeda": _C.format('<circle cx="32" cy="32" r="22" stroke="#f2b705"/><path d="M38 22c-2-3-12-4-12 2 0 7 14 4 14 11 0 6-11 6-14 2M32 16v6M32 42v6" stroke="#2f9e44"/>'),
}

# Capítulo -> rabisco. Capítulo novo sem entrada aqui usa "lupa".
CHAPTER_ICONS = {
    "1.1": "notebook", "1.2": "caixa", "1.3": "aspas", "1.4": "lista", "1.5": "ciclo",
    "1.6": "bifurca", "2.2": "chave", "2.3": "engrenagem", "2.4": "panda", "2.5": "vassoura",
    "3.1": "lupa", "3.2": "buraco", "3.3": "funil", "3.4": "grafico", "3.5": "calendario",
    "3.6": "engrenagem", "3.7": "engrenagem", "4.1": "sino", "4.2": "dado", "4.3": "balanca",
    "5.1": "terminal", "5.2": "terminal", "5.4": "engrenagem", "5.5": "terminal",
    "6.1": "lupa", "6.2": "engrenagem", "7.1": "banco", "7.2": "banco", "7.3": "banco",
    "7.4": "banco", "7.5": "pessoas", "7.6": "banco", "8.1": "funil", "8.2": "pessoas",
    "8.3": "moeda", "8.4": "pessoas", "9.1": "balanca",
}


def icon(kind: str) -> str:
    return ICONS.get(kind, "")


def chapter_doodle(cap: str) -> str:
    return CHAPTER_DOODLES.get(CHAPTER_ICONS.get(cap, "lupa"), "")


def render_desenhos(body: str) -> str:
    """```desenho nome\nlegenda``` -> figura SVG com legenda manuscrita."""
    def repl(m):
        name = m.group(1).strip()
        caption = m.group(2).strip()
        f = DESENHOS / f"{name}.svg"
        if not f.exists():
            return f'\n<p class="falta-desenho">[desenho "{html.escape(name)}" não encontrado]</p>\n'
        svg = f.read_text(encoding="utf-8")
        cap = f'<figcaption>{html.escape(caption)}</figcaption>' if caption else ""
        return f'\n<figure class="desenho">{svg}{cap}</figure>\n'

    return re.sub(r"```desenho[ \t]+([\w-]+)\n(.*?)```", repl, body, flags=re.S)


def corrigido_html(title: str, inner_html: str) -> str:
    title = title or "Opa, corrigindo!"
    return (
        '\n<div class="corrigido"><span class="fita"></span>'
        f'<div class="corr-t">✎ {html.escape(title)}</div>{inner_html}</div>\n'
    )
