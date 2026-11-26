# Assistente de estudos · Análise de Dados (TripleTen)

Três partes:

1. **Guia em PDF** (`Guia_de_Estudos_DA.pdf`): sumário clicável, botão "↑ Sumário" em todas as páginas, capítulos por sprint, dicionário de fórmulas e de siglas (A–Z).
2. **Quiz diário** (`quiz/`): publicado como artifact no claude.ai, com ofensiva, XP e repetição espaçada.
3. **Dúvida de colega**: tarefa agendada `duvida-de-colega` no app Claude (dias úteis, ~10:37 e ~15:37). O Clawd on Desk mostra o balão.

## Como atualizar o guia

1. Novo capítulo no Drive (`G:\My Drive\Triple Ten`) → peça ao Claude para transcrever para `content/sN/N.M-nome.md`.
2. Fórmulas e siglas novas vão em `data/formulas.yaml` e `data/siglas.yaml`.
3. Gere o PDF:

```powershell
python build/build_pdf.py
```

Erros encontrados nas anotações ficam registrados em `REVISAO.md`.
