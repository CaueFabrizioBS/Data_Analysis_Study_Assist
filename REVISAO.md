# Revisão das anotações

Coisas que achei nas anotações do Drive enquanto montava o material. No PDF já está a versão corrigida; aqui fica o registro para você conferir e, se quiser, ajustar o caderno.

## Erros corrigidos

| Onde | Anotação | Correção |
|---|---|---|
| 1.2 Operações aritméticas | PEMDAS com "potência = `%`" | P é **Parênteses**, E é **Expoentes** (`**`). `%` é módulo (resto da divisão), fica no nível da multiplicação/divisão. |
| 1.2 Conversão de tipos | "converter inteiro em float com `int()` e o contrário com `float()`" | Invertido: `int()` converte **para** inteiro, `float()` **para** decimal. |
| 1.2 String → int | "se ainda estivesse em int não seria possível essa soma" | Se ainda estivesse em **string** não seria possível. |
| 1.3 Índices | "`word[6]` obtém a 6ª letra" | É a 7ª letra, porque o índice começa em 0. |
| 1.3 .format | "pode-se atribuir uma letra para cada f-string" | Ali é `.format()` com nomes (`{n}`, `{a}`), não f-string. |
| 1.5 Listas aninhadas | "`print(variável[][])`: primeiro coluna, depois linha" | Primeiro **linha**, depois **coluna** (na página de listas você anotou certo). |
| 2.2 Dicionários | `financial_info.get['Walt Disney'] == None` | `get` é método, leva parênteses: `.get('Walt Disney')`. Com colchetes dá erro. Melhor ainda: `'Walt Disney' not in financial_info`. |
| 2.4 count() | "`duration_threshold = 180`: músicas com até 180 seg" | O código usa `>`, então conta as músicas com **mais** de 180 segundos. |
| 2.5 dropna(subset) | "retire as linhas com valores zerados em todas essas colunas" | Remove as linhas com valor **ausente (NaN)** em **qualquer** uma dessas colunas. Zero não é ausente para o pandas. |
| 3.1 Leitura de CSV | "valores separados por `\|` tabulação" | `\|` é a barra vertical (*pipe*). Tabulação é `\t`. |
| 3.4 Visualização | "Matplotlib, dentro dela existem Seaborn, Plotly, Pyplot" | `pyplot` é um módulo do matplotlib. Seaborn é construído em cima do matplotlib. Plotly é uma biblioteca separada. |
| 3.5 Datas | `11-03-01 17:34:15` com `%m-%d-%Y` | Ano de 2 dígitos é `%y`. `%Y` espera 4 dígitos. |
| 4.1 Boxplot | "bigode da publicidade contextual é bem maior, ou seja, atinge bem mais gente" | Bigode longo à direita = alguns clientes gastam muito mais (assimetria). Não mede alcance. |
| 4.1 Três sigmas | "99,7% dos valores em 1 dos 6 desvios padrão" | 99,7% ficam **entre** μ − 3σ e μ + 3σ (os seis desvios juntos). |
| 4.2 Combinação | "k = quantidade de combinações" | k é quantos itens você escolhe. O resultado da fórmula é a quantidade de combinações. |
| 4.2 Distribuições | Normal "discreta ou contínua"; uniforme "contínua" com exemplo do dado | Normal é contínua. Uniforme pode ser discreta ou contínua; o dado é uniforme discreta. |
| 4.3 TCL | "quanto maior a amostra, mais a média amostral parece com a da população" | Isso é a lei dos grandes números. O TCL diz que as médias amostrais formam um sino em torno da média da população. |
| 4.3 Valor-p | "valor-p = média − valor a comparar" | Valor-p é uma probabilidade. A diferença em erros padrão é a estatística t. |
| 5.1 CLI | `pwd` = "print working disk", `cd` = "change disk" | *print working **directory*** e *change **directory***. |
| 5.1 CLI | "`.exemplo` para diretório e `..exemplo` para arquivo" | Nome começando com `.` é oculto (arquivo ou pasta). `.` sozinho é a pasta atual, `..` a pasta de cima. |
| 5.1 find | "`-iname`: o nome depois vem todo minúsculo"; "`-mtime`: dias em que foi criado"; "`-cmin` para minutos" | `-iname` ignora maiúscula/minúscula. `-mtime -2` = **modificado** há menos de 2 dias. O equivalente em minutos é `-mmin`. |
| 5.1 grep | "para todos os arquivos usamos `*` depois da palavra" | O `*` é o coringa dos **arquivos** (todos da pasta), não faz parte da palavra buscada. |
| 5.1 Variáveis | "para criá-las usamos `echo` ou `printenv`" | Cria com `NOME="valor"` (ou `export`). `echo $NOME` e `printenv` só mostram. |
| 5.1 Pipes | "pipe funciona como filtro ou como um 'and'" | O pipe passa a saída de um comando como entrada do próximo. |
| 6.1 Erros | "IndexError: elemento inexistente em dicionário ou lista" | Em lista é `IndexError`. Em dicionário é `KeyError`. |
| 5.4 Classes | "dicionários são menos flexíveis e não são manipuláveis" | Dicionários são mutáveis. A vantagem da classe é juntar dados e métodos num molde. |
| 5.4 staticmethod | "usamos para buscar informação de fora (internet)" | É um método que não usa nem `self` nem `cls`. Buscar na internet foi só o exemplo. |
| 5.4 classmethod | "para concatenar informações da classe" | Recebe `cls`; o uso típico é um jeito alternativo de criar objetos (`from_string`). |
| 5.4 split | "não há algo para separar, devemos detalhar dentro do split()" | `split()` sem argumento já separa por espaços. `'ABC 10 1.5'.split()` funciona. |
| 5.4 JSON/YAML | "servem para puxar infos da internet; YAML é um conjunto de JSON"; "`dump` adiciona conteúdo à lista" | São formatos de dados (texto). `dump` grava num arquivo, `dumps` gera string. |
| 5.4 API | "chave segura chamada API" | API é a interface. A chave é a **chave de API** (token). |
| 4.3 Região crítica | "P(800 ≤ X ≤ 1200) = 95,45% → de H₁" | Os 95,45% do meio são a região de não rejeitar H₀. |

## Material faltando

(preenchido conforme avanço)
