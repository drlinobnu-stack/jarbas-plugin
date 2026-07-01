---
name: jarbas-conclusao
description: >
  Escreve a Discussão/Conclusão e responde aos quesitos de um laudo de
  AUXÍLIO-ACIDENTE (réu INSS) já examinado, trabalhando DIRETAMENTE sobre o ODT
  pronto (exame físico preenchido, seções 7 Discussão/Conclusão e 8 Quesitos em
  branco), sem mexer no resto. Lê o laudo e, quando anexados, os autos (quesitos
  faltantes, exames não transcritos, prontuário INSS). Decide o tipo de conclusão
  pelos achados (exame físico, imagem, profissiografia), redige no estilo exato do
  Dr. Lino com DID, consolidação e enquadramento no Decreto 3048/99, e responde
  todos os quesitos (juízo, autor, réu). Preserva o cabeçalho (logo) e gera o ODT
  final pelo script gerar_conclusao_odt.py. Use com "/jarbas-conclusao",
  "conclusão do laudo", "redigir a discussão e conclusão", "finalizar o laudo".
metadata:
  version: "1.0.0 (porte da conclusao1 v4.2.0 para o plugin JARBAS, fluxo ODT nativo)"
  author: "Dr. Francisco Salvador Brod Lino"
  command: "/jarbas-conclusao"
---

# Skill: /jarbas-conclusao — Redigir Conclusão, Responder Quesitos e Finalizar Laudo (ODT)

Ler o laudo pericial com exame físico já preenchido, ler os autos obrigatórios,
redigir a Discussão/Conclusão no estilo exato do Dr. Lino, responder todos os
quesitos e gerar o laudo **COMPLETO em .odt** com todas as correções aplicadas.
O arquivo entregue é sempre o laudo inteiro em .odt — nunca apenas seções isoladas.

---


## REGRA ABSOLUTA E GLOBAL: PORTUGUÊS PERFEITO — ACENTUAÇÃO COMPLETA OBRIGATÓRIA

> **TODO texto gerado deve usar português correto com acentuação completa.**
> - Cedilha: ç (ação, proteção, função, execução, lesão)
> - Til: ã, õ (não, mão, coração, lesões, condições)
> - Acento agudo: á, é, í, ó, ú (análise, médico, perícia, órgão, próximo)
> - Acento circunflexo: â, ê, ô (exame, após, três, cômputo)
> - Crase: à (à direita, à esquerda, à distância)
>
> **NUNCA escrever texto sem acentuação.** SEMPRE revisar o documento completo antes de entregar.
> Ao gerar JSON, usar **sempre** `ensure_ascii=False` para preservar os caracteres Unicode.

---

## REGRA ABSOLUTA E GLOBAL: TRAVESSÕES PROIBIDOS NO TEXTO NOVO

> **NUNCA usar travessão ( — ), meia-risca ( – ) ou hífen solto ( - ) no
> meio de frases, títulos ou listas em QUALQUER TEXTO NOVO escrito por
> Claude: conclusão, respostas aos quesitos, textos gerados ou inseridos.**
>
> **PORÉM: travessões e meias-riscas JÁ EXISTENTES no laudo original devem
> ser PRESERVADOS. O script NÃO remove travessões do documento existente.**
>
> Substituições obrigatórias apenas em texto NOVO:
> - Travessão explicativo: usar vírgula ou dois-pontos
>   Errado: "O exame — realizado em 2024 — revelou..."
>   Certo: "O exame, realizado em 2024, revelou..."
> - Travessão em título: usar dois-pontos ou preposição
>   Errado: "Nexo Causal — Discussão"
>   Certo: "Nexo Causal: Discussão"
> - Travessão enumerativo: usar dois-pontos seguido de novo parágrafo

---

## REGRA ABSOLUTA E GLOBAL: DATAS NO FORMATO dd.mm.aaaa

> **SEMPRE usar ponto como separador de datas. NUNCA usar barra (/).**
>
> - Início de frase: "No dia 02.02.2022, o autor..."
> - Meio de frase: "...acidente ocorrido no dia 02.02.2022..."
> - **NUNCA escrever "em dia XX.XX.XXXX". A preposição correta é sempre "no dia": "no dia XX.XX.XXXX" ou "no dia XX de mês de XXXX".** O script `gerar_conclusao_odt.py` insere "dia" antes de datas dd.mm.aaaa; por isso, no texto de entrada já escrever "no dia XX.XX.XXXX" / "No dia..." (o script vê o "dia" e não duplica). Depois de gerar, varrer o XML e trocar qualquer "em dia"→"no dia" e "Em dia"→"No dia" remanescente. Confirmado pelo Dr. em 01/07/2026 (laudo Junior Cezar Alves).
> - Ao revisar texto existente no laudo: substituir toda barra por ponto nas datas
> - Exceção: data da cidade na página 1 permanece por extenso
>   ("Blumenau, 29 de maio de 2026")

---

## REGRA ABSOLUTA E GLOBAL: RESPOSTAS AOS QUESITOS — OBJETIVAS

> Responder **somente o que foi perguntado**. Máximo de 1 a 3 frases por resposta.
> - Se sim/não: começar com "Sim." ou "Não." + no máximo uma frase de fundamentação
> - Não repetir informações de outros quesitos
> - Não elaborar dissertações onde cabe uma frase objetiva
> - Não listar fatores redundantes (idade, escolaridade, sequelas) em toda resposta

---

## Quando acionar

- Comando `/jarbas-conclusao` (ou pelo app SIMAS, área Perícia judicial > Conclusão)
- Dr. Lino diz "preencher a conclusão", "redigir a discussão", "finalizar o laudo"
- Dr. Lino anexa laudo ODT com as seções 7 (Discussão/Conclusão) e 8 (Quesitos) em branco
- Dr. Lino diz "responder quesitos e conclusão juntos"

---

## Fluxo obrigatório

Execute os passos em ordem. Não pule etapas.

### Passo 1 — Verificar arquivos anexados

- **Laudo (.docx ou PDF)** — obrigatório. Deve conter exame físico preenchido e
  seções de Discussão/Conclusão e Quesitos em branco ou com "XXX".
  Se não estiver anexado, solicitar ao Dr. Lino.

- **Autos do processo (PDF)** — **fortemente recomendados** (no app SIMAS são um campo opcional). Quando anexados, os autos servem para:
  - Verificar se há quesitos de alguma parte que a secretária não transcreveu no laudo
  - Encontrar exames complementares dos autos não listados no laudo
  - Ler o prontuário do INSS (geralmente nas primeiras folhas dos autos)
  - Confirmar dados de benefícios, DIB, DCB, espécie
  - Se os autos não estiverem anexados, solicitar: "Para finalizar o laudo com
    segurança, preciso também dos autos do processo em PDF. Por favor, anexe-os."

### Passo 2 — Ler o laudo completo e extrair dados clínicos

1. Localizar o laudo .odt e os autos na pasta do caso (o caminho é informado no
   prompt; no app SIMAS é a pasta `_casos_simas/<timestamp>/`).
2. Extrair o texto completo do laudo ODT lendo o content.xml:
   ```bash
   python3 -c "
   import zipfile, re, html
   x = zipfile.ZipFile('LAUDO.odt').read('content.xml').decode('utf-8')
   x = re.sub(r'</text:[ph]>', chr(10), x)
   print(html.unescape(re.sub(r'<[^>]+>', '', x)))
   "
   ```

3. Identificar e registrar os seguintes dados clínicos:

   **Dados do processo:**
   - Número dos autos (cabeçalho)
   - Nome do periciando (e gênero: autor/autora)
   - Vara e comarca
   - Data e local da perícia
   - Finalidade (trabalhista, previdenciária, cível)
   - Réu (empresa, INSS, etc.)

   **Dados clínicos:**
   - Queixa principal e histórico relatado (anamnese)
   - Diagnóstico(s) e CID(s) mencionados no laudo
   - Data do acidente ou início da doença
   - Tratamentos realizados (cirurgias, sessões de fisioterapia, etc.)
   - Período(s) de benefício: DIB, DCB, espécie, NB
   - Achados do exame físico (amplitude de movimento, força, sensibilidade,
     sinais especiais, cicatrizes, etc.)
   - Exames complementares mencionados no laudo
   - Profissão e atividades laborais do periciando na época do acidente e atualmente
   - Lateralidade (destro/canhoto, membro dominante)

### Passo 3 — Ler os autos e cruzar com o laudo

1. Ler os autos (PDF) com a ferramenta de leitura de arquivos (Read), que abre PDF
   diretamente. Esta máquina NÃO tem `pdftotext`/`pdfinfo` (poppler) instalado.

2. **Prontuário do INSS:** Localizar as folhas de prontuário do INSS (geralmente
   identificadas na tabela de documentos do laudo como "Prontuário INSS").
   Ler estas folhas com atenção. O prontuário INSS frequentemente contém:
   - Diagnósticos e CIDs registrados pela Previdência
   - Datas de atendimento médico-pericial do INSS
   - Confirmação de nexo acidentário ou previdenciário
   - Informações sobre capacidade laborativa em avaliações anteriores
   - Dados de benefícios (espécie, DIB, DCB) que confirmam ou complementam o laudo

3. **Quesitos faltantes:** Varrer os autos em busca de quesitos de todas as partes.
   Comparar com os quesitos já listados no laudo. Se encontrar quesitos que não
   constam no laudo (common error — secretária pode não ter visto quesitos de
   alguma parte), registrar esses quesitos para responder e acrescentar ao laudo.

4. **Exames não transcritos:** Verificar se nos autos há laudos de exames
   complementares (RX, ultrassom, RM, eletromiografia, etc.) que não foram
   listados na seção 4.2 (Exames complementares) do laudo. Se encontrar,
   registrar as conclusões para usar na redação da conclusão.

5. Indexar informações adicionais relevantes: histórico médico, atestados,
   laudos de peritos anteriores, registros de CAT (Comunicação de Acidente de Trabalho).

### Passo 4 — VERIFICAÇÕES E CORREÇÕES AUTOMÁTICAS OBRIGATÓRIAS

Executar todas antes de redigir a conclusão. Registrar cada correção.

#### 4.1 — Data da página 1

1. Localizar a data na página 1 (formato: "Cidade, DD de mês de AAAA").
2. Comparar com a data de hoje.
3. Se diferentes, atualizar para a data atual por extenso.
4. Registrar: "Data corrigida de [original] para [atual]" ou "Data confirmada".

#### 4.2 — Erros ortográficos e de digitação

1. Percorrer todo o texto preenchido (exceto as seções XXX) em busca de:
   - Erros ortográficos evidentes em português
   - Palavras duplicadas ("o o paciente", "de de")
   - Letras trocadas em termos médico-jurídicos
   - Concordância grosseiramente errada
2. Corrigir diretamente no documento.
3. Registrar lista resumida.

#### 4.3 — Número de páginas nas Considerações Finais (contagem automática)

1. Localizar "Considerações Finais" e o marcador XXXX/XXXXX do total de páginas.
2. O script `gerar_conclusao_odt.py` detecta automaticamente o número real de páginas
   convertendo o .docx para PDF via LibreOffice e lendo o metadado `Pages`.
3. Substituir "XXXXX" pelo número real (algarismo + extenso entre parênteses).
4. **Não tentar estimar manualmente** — o script faz isso após inserir a conclusão
   e as respostas, para que o número final já reflita o documento completo.
5. Registrar: "Páginas detectadas automaticamente: [N]".

#### 4.4 — Número dos autos nas Considerações Finais

1. Extrair número dos autos do cabeçalho das páginas iniciais.
2. Verificar se o mesmo número está citado nas Considerações Finais.
3. Se divergir, corrigir para o número do cabeçalho.
4. Registrar: "Autos confirmados: [número]" ou "Autos corrigido".

#### 4.5 — Travessões no texto existente: PRESERVAR

Os travessões ( — ), meias-riscas ( – ) e hifens já presentes no laudo
original NÃO devem ser removidos ou alterados. O script gerar_conclusao.py
não modifica o texto existente do laudo quanto a travessões.
A proibição de travessões aplica-se SOMENTE ao texto NOVO inserido por
Claude (conclusão redigida e respostas aos quesitos).

### Passo 5 — Redigir a Discussão e Conclusão

Redigir o texto completo da seção "Discussão / Conclusão" seguindo **exatamente**
o estilo do Dr. Francisco Lino, conforme os laudos modelo.

**PRIMEIRO: identificar o tipo de incapacidade** a partir do exame físico, diagnóstico
e indicações do próprio Dr. Lino no laudo (ele frequentemente deixa uma nota como
"incapacidade total e temporária" ou "incapacidade parcial e permanente").
O tipo determina **toda a estrutura da conclusão**.

---

## MODELO A — Incapacidade Parcial e Permanente (Auxílio-Acidente)

Este é o modelo MAIS COMUM. Usar quando o laudo indica sequela consolidada com
limitação funcional permanente decorrente de acidente de trabalho (típico ou atípico).

**Laudo de referência validado:** Yeissica Josefina Marcano Velasquez, junho/2026.

### Estrutura exata dos parágrafos (reproduzir fielmente):

**Parágrafo 1 — Fato gerador e diagnóstico:**
Uma única frase curta. SEM "quando" ou descrição detalhada da circunstância.

*Variante A — Acidente de trabalho / percurso (evento traumático agudo):*
"[O autor / A autora] teve acidente de [trabalho / percurso] em [data dd.mm.aaaa][,
equiparado a acidente de trabalho,] com [diagnóstico] (CID [X])."
Exemplo: "A autora teve acidente de trabalho em 26.07.2023 com fratura da
diáfise proximal do úmero esquerdo (CID S42.2)."
Exemplo com amputação: "O autor teve acidente de trabalho em 15.12.2000, com amputação
total do 5º quirodáctilo da mão direita (CID Z89.1)."

*Variante B — Doença profissional / ocupacional (início gradual, sem trauma agudo):*
"[O autor / A autora] é portador(a) de doença profissional diagnosticada como
[diagnóstico] (CID [X]), com nexo causal com a atividade laboral habitual de
[profissão], envolvendo [descrição concreta dos movimentos/exposição/esforços]."
Exemplo: "O autor é portador de doença profissional diagnosticada como síndrome do
manguito rotador esquerdo com ruptura tendínea (CID M75.1), com nexo causal com a
atividade laboral habitual de estampador, envolvendo movimentos repetitivos de
abdução e elevação do membro superior esquerdo."
Usar quando: início gradual (meses/anos), sem evento traumático específico.

**Parágrafo 2 — Tratamento e sequela:**
Construção obrigatória — começa com "Embora", NÃO com "Foi realizado":
"Embora tenha realizado o devido tratamento, restou com limitação funcional em grau [X]
para o [segmento anatômico] [lado se aplicável]."
Grau: leve / médio / grave / mínimo — conforme achados do exame físico.
Exemplo validado: "Embora tenha realizado o devido tratamento, restou com limitação
funcional em grau médio para o ombro esquerdo."

**Parágrafo 3 — Repercussão profissional:**
Construção obrigatória — usa "Tal sequela", NÃO "Tal quadro". NÃO incluir "em grau X".
"Tal sequela gera maior dificuldade para o trabalho habitual ([lista das tarefas
concretas e específicas da profissão que são afetadas])."
As tarefas devem ser extraídas do histórico da profissão descrito na anamnese, com
descrição funcional concreta das dificuldades.
Exemplo validado: "Tal sequela gera maior dificuldade para o trabalho habitual (maior
dificuldade para buscar materiais nas prateleiras para levar para as costureiras, fazer
certas costuras à mão, maior dificuldade para o manuseio de peças do vestuário com o
membro superior esquerdo)."

**Parágrafo 4 — Boilerplate obrigatório:**
SEMPRE usar este texto exato:
"Com base nas informações obtidas na anamnese durante a expertise médico pericial,
tomando-se por base a minudente análise retrospectiva documental e notadamente pelo
exame físico geral e segmentar descrito no corpo do laudo técnico, como prerrogativa do
Perito deste Juízo, este avaliador técnico de confiança do Magistrado conclui que:"

**Parágrafo 5 — Enquadramento no Decreto 3048/99:**
"[O autor / A autora] possui sequela que se enquadra tecnicamente no quadro 6 do Anexo
III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."
ATENÇÃO: NÃO especificar alínea. Apenas "quadro 6". Sem dois-pontos no final.

**Seção "Dados de interesse pericial:" (após os parágrafos acima):**

1. DID:
   *Para acidente:* "A Data de Início da Doença (DID) é estimada na data do acidente,
   em dia [data dd.mm.aaaa]."
   *Para doença profissional com data de início dos sintomas conhecida:*
   "A Data de Início da Doença (DID) é estimada no início dos sintomas, em [período]."
   *Para doença profissional sem data precisa:* "A Data de Início da Doença (DID) é de
   difícil precisão, estimada em [data/período], com base nos documentos disponíveis."

2. Incapacidade:
   *Para acidente:* "Existiu uma incapacidade total e temporária entre o acidente em dia
   [data] e a DCB em dia [data]. Após a DCB passou a existir uma incapacidade parcial e
   permanente a qual não impede [o autor / a autora] de trabalhar em sua atividade
   habitual, porém com maior dificuldade para algumas operações."

   *Para doença profissional:* "Existiu uma incapacidade total e temporária entre o
   afastamento em dia [data início benefício] e a DCB em dia [data DCB]. Após a DCB
   passou a existir uma incapacidade parcial e permanente a qual não impede [o autor /
   a autora] de trabalhar em sua atividade habitual, porém com maior dificuldade para
   algumas operações."
   (Nota: usar "afastamento" em vez de "acidente" para doença profissional)

3. Consolidação — formato EXATO validado (3 parágrafos separados):
   Parágrafo a: "3.Quanto a Consolidação:"
   (Nota: "Quanto a" sem acento em "a". "3." colado ao "Quanto".)
   Parágrafo b: "- Segundo a ABMLPM na descrição de Conceitos Médicos Legais da Tabela
   Brasileira para Apuração do Dano corporal, temos que:"
   (ATENÇÃO: o parágrafo começa com "- Segundo", com hífen e espaço antes de "Segundo")
   Parágrafo c: "Consolidação médico-legal da lesão, é quando, finalizados os
   tratamentos, esgotando-se as medidas terapêuticas atuais e disponíveis, não se
   vislumbrando evolução para melhora da lesão, configurando-se a sequela, um dano
   permanente."
   (ATENÇÃO: SEM hífen antes de "Consolidação" — diferente do parágrafo b que TEM "- Segundo")
   Parágrafo d: "No caso em tela, estima-se a consolidação do quadro na DCB, em
   [data], pelo critério da compatibilidade anátomo clínica."
   ATENÇÃO: NÃO colocar "dia" antes da data de consolidação (diferente dos itens 1 e 2).
   **Laudo validado:** Nelson Heinert (junho/2026) — usar como referência definitiva de estrutura e espaçamento.

---

## MODELO B — Incapacidade Total e Temporária

Usar quando o quadro clínico não está consolidado, o tratamento ainda está em curso
(aguarda cirurgia, em reabilitação ativa, etc.) e não há sequela definitiva ainda.
Casos de doença com afastamento em curso, espécie B31 ou B91 sem cessação definitiva.

**Atenção: estrutura completamente diferente do Modelo A.**
Não usar o parágrafo de transição boilerplate. Não usar Decreto 3048/99.

**Parágrafo 1 — Diagnóstico e quadro clínico atual:**
Descrever o diagnóstico com CID e a condição clínica ao exame.
Construção: "[O/A] [autor/autora] possui [quadro de] [diagnóstico] ([CID]) [localização]
[a qual/o qual] se mostra [bem ativa ao atual exame pericial / em fase ativa / etc.]."

**Parágrafo 2 — Tipo de incapacidade:**
Sempre esta frase exata:
"Tal quadro gera uma incapacidade total e temporária para o trabalho habitual."

**Parágrafo 3 — Status do tratamento e prognóstico:**
Descrever o tratamento em andamento e a estimativa de duração.
Exemplos:
- "[O/A] [autor/autora] já está na fila para o procedimento cirúrgico e estima-se um
  período de mais [prazo] de incapacidade laborativa."
- "[O/A] [autor/autora] encontra-se em tratamento [clínico/fisioterápico] e estima-se
  um período de [prazo] para reavaliação."

**Parágrafo 4 — Afirmação de incapacidade na DCB:**
Sempre esta construção:
"Com base nos dados disponíveis para análise é possível afirmar a existência de
incapacidade quando da DCB em [data da última DCB documentada]."

**Seção "Dados de interesse pericial:":**

1. DID: "A Data de Início da Doença (DID) é estimada em [data]."

2. DII: "A Data de Início da Incapacidade (DII) é estimada em [data]."
   (A DII é diferente da DID: a DID é quando a doença começou; a DII é quando
   a incapacidade laborativa começou, geralmente coincide com o primeiro benefício.)

3. Nexo de causa: "Quanto ao nexo de causa, [descrever se é nexo direto, concausal
   ou ausente]. Exemplo: 'o quadro [diagnóstico] é multicausal, porém o trabalho
   realizado participa como um dos mecanismos causais, sendo assim uma concausa.'"

---

## Identificação do tipo pelo laudo

| Indicador no laudo | Tipo |
|---|---|
| "incapacidade total e temporária" | Modelo B |
| "incapacidade parcial e permanente" | Modelo A |
| Enquadramento Decreto 3048/99 mencionado | Modelo A |
| Aguardando cirurgia / tratamento ativo | Modelo B |
| Sequela consolidada / sem perspectiva de melhora | Modelo A |
| DII mencionada junto com DID | Modelo B |
| Consolidação mencionada | Modelo A |

Se o tipo não estiver explícito, analisar o exame físico e o pedido da petição:
auxílio-acidente → Modelo A; auxílio-doença continuado → Modelo B.

---

## Graus de limitação funcional (Modelo A):
| Grau | Critério clínico |
|------|-----------------|
| Leve | Limitação presente mas realiza a maioria das atividades habituais com restrição em movimentos de amplitude máxima |
| Médio | Limitação significativa dos arcos de movimento, com restrição em atividades moderadas |
| Máximo/Intenso | Limitação grave, com restrição mesmo em atividades básicas do segmento |

---

#### Regras de redação (ambos os modelos):
- Linguagem técnico-pericial, objetiva, impessoal
- Sem travessões no texto novo redigido
- Fundamentar cada afirmação nos achados do laudo ou dos autos
- Nunca inventar dados não presentes no laudo ou nos autos
- Usar gênero correto (autor/autora) conforme o periciando

### Passo 6 — Responder todos os quesitos

Responder os quesitos de todas as partes: Juízo, Autor/Reclamante, Réu/Reclamado/INSS.
Se nos autos foram encontrados quesitos não transcritos no laudo (vide Passo 3),
incluí-los e respondê-los também.

**Estilo das respostas — baseado no laudo validado Yeissica/junho-2026:**
- Respostas curtas e diretas; máximo 1 a 2 frases
- "Mais detalhes, vide item Discussão e Conclusão desse laudo." é resposta válida e preferível
  quando o quesito pede o que já está na conclusão
- "Vide item 3 do laudo." para questões de profissiografia
- "Prejudicado." para quesitos sobre incapacidade total permanente (que não existe)
- "Não é caso para reabilitar, pode fazer a mesma atividade que desenvolvia na época
  do acidente, porém com maior dificuldade para algumas operações." para quesitos 8/8.1/8.2
- "Gera limitação para atividades pontuais." para quesito sobre trabalho doméstico (Q15)
- "A limitação de funcionalidade claramente detectada nas manobras propedêuticas do
  exame pericial é que ampara tal divergência. Mais detalhes, vide item Discussão e
  Conclusão desse laudo." para quesito de divergência com laudo administrativo (Q16)

**Quesitos específicos com resposta padrão validada:**

| Quesito | Resposta padrão |
|---|---|
| Q1 autora (ciência art. 473 CPC) | "Sim. Este perito tem ciência de tal disposição e todas as respostas estão fundamentadas nos achados periciais." |
| Q5 autora (concordar com legislação) | "Não é objetivo deste laudo concordar ou discordar da legislação." |
| Q réu 1 (diagnóstico/CID) | Repetir P1 + P2 da conclusão na íntegra |
| Q réu 2 (causa) | Marcar 2.7 com (X); justificativa: mais detalhes, vide item Discussão e Conclusão desse laudo |
| Q réu 6 (data início redução) | "Na consolidação em [data], pelo critério da compatibilidade anátomo clínica." |
| Q réu 8/8.1/8.2 (reabilitação) | "Não é caso para reabilitar, pode fazer a mesma atividade que desenvolvia na época do acidente, porém com maior dificuldade para algumas operações." |
| Q réu 9/10/11 (incap. total permanente) | "Prejudicado." |
| Q réu 15 (trabalho doméstico) | "Gera limitação para atividades pontuais." |

**Por tipo de quesito geral:**
| Tipo | Como responder |
|------|---------------|
| Quesito pede o que já está na conclusão | "Mais detalhes, vide item Discussão e Conclusão desse laudo." |
| Quesito sobre profissiografia | "Sim, vide item 3 do laudo." |
| Incapacidade para a profissão | Tipo (parcial/total) + "Mais detalhes, vide item Discussão e Conclusão desse laudo." |
| Permanente ou temporária | "Permanente (X)." |
| Incapacita para toda atividade | "Prejudicado." |
| Necessita assistência permanente | "Prejudicado." |
| Quesito sobre reabilitação profissional | "Não é caso para reabilitar..." |
| **Concordar/discordar de legislação** | "Não é objetivo deste laudo concordar ou discordar da legislação." |
| **Esforço físico excessivo** | "Ninguém está apto para atividades com esforços físicos excessivos e constantes, para balizar tais situações existe a NR 17 que versa sobre ergonomia e suas implicações no trabalho." |
| **Igualdade no mercado de trabalho** | "Prejudicado, não é objetivo desta perícia tal avaliação." |
| **Adaptação ergonômica** | "Prejudicado, não é objetivo desta perícia tal avaliação." |

Salvar respostas em `quesitos-respostas.json`:
```json
{
  "quesitos_juizo": [],
  "quesitos_autor": [
    {"numero": "1", "texto": "...", "resposta": "..."}
  ],
  "quesitos_reu": [
    {"numero": "1", "texto": "...", "resposta": "..."}
  ]
}
```

### Passo 7 — Gerar o ODT final (script nativo, preserva o cabeçalho)

1. Salvar o texto da Discussão/Conclusão em um arquivo .txt, com os blocos
   separados por UMA linha em branco (o script usa isso para o espaçamento; ele
   coloca 2 linhas em branco antes de "Dados de interesse pericial:").

2. Salvar as respostas em um JSON, NA MESMA ORDEM em que os "Resposta:" aparecem
   no laudo (juízo, depois autor, depois réu):
   ```json
   {
     "quesitos_juizo": [],
     "quesitos_autor": [{"numero": "1", "resposta": "..."}],
     "quesitos_reu":   [{"numero": "1", "resposta": "..."}]
   }
   ```
   Quesito sem resposta possível: deixar `"resposta": ""` (fica em branco) ou
   `"resposta": "Prejudicado."`. NUNCA "Não se aplica".

3. Rodar o gerador ODT (trabalha sobre uma cópia, não altera o original):
   ```bash
   python3 ~/.claude/scripts/gerar_conclusao_odt.py \
     --laudo  "LAUDO_ENTRADA.odt" \
     --conclusao  conclusao-texto.txt \
     --respostas  quesitos-respostas.json \
     --saida  "CAMINHO_DE_SAIDA.odt" \
     --autos  "NUMERO-DOS-AUTOS"
   ```

O script `gerar_conclusao_odt.py`:
- Insere os blocos da conclusão entre "Discussão / Conclusão:" e "Quesitos:",
  com 1 linha em branco entre blocos e 2 antes de "Dados de interesse pericial:".
- Preenche cada "Resposta:" na ordem, em itálico (estilo CONC_IT).
- Em texto NOVO: remove travessões, troca "Não se aplica" por "Prejudicado",
  põe "dia"/"Dia" antes de datas dd.mm.aaaa.
- Corrige a data da página 1 para hoje (se diferente).
- Substitui "xxx (xxx)" das Considerações finais pela contagem real de folhas
  (converte o ODT para PDF via LibreOffice e conta as páginas; não usa poppler).
- Re-zipa o ODT cru (mimetype primeiro) preservando o cabeçalho/logo e todo o
  resto. NUNCA reconverte o ODT pelo LibreOffice (isso quebraria o cabeçalho).

As quebras de página antes de Considerações finais, Bibliografia e Responsável já
vêm do template do JARBAS e são preservadas.

### Passo 8 — IMC e REVISÃO FINAL OBRIGATÓRIA (agente revisor-laudo)

**IMC:** o laudo de conclusão já vem com o exame físico preenchido. A partir do peso e
da altura do exame, calcule o IMC (peso dividido pela altura ao quadrado), preencha o
campo "IMC:" com o valor e, na lista de classificação, mantenha SOMENTE a faixa em que
o periciado se enquadra, apagando as demais. Nunca pode sobrar mais de uma faixa.

**Revisão final:** antes de entregar, rode SEMPRE o subagente `revisor-laudo` (ferramenta
Task/Agent) sobre o ODT gerado. Ele renderiza o PDF, percorre todas as páginas e confere
a checklist completa (ortografia, gênero, espaçamentos, nº de páginas, bibliografia não
cortada, datas, IMC, formatação da conclusão e dos quesitos). Se o veredito for AJUSTAR,
aplique as correções apontadas e rode o revisor de novo, até o veredito PRONTO (no máximo
3 rodadas). Só então avise o Dr. que o laudo está pronto. Esta etapa é obrigatória e nunca
deve ser pulada.

### Passo 9 — Entregar ao usuário

Entregar **sempre apenas o .odt** (laudo completo). Responder com link direto e resumo:

```
Laudo finalizado.

Conteúdo inserido:
- Discussão/Conclusão: [N parágrafos]
- Quesitos respondidos: [X preenchidos, Y em branco]
- Quesitos adicionais encontrados nos autos: [N] (se houver)

Correções automáticas:
- Data: [confirmada / corrigida para DD de mês de AAAA]
- Ortografia: [N erros corrigidos / nenhum encontrado]
- Páginas nas Considerações Finais: [N páginas]
- Número dos autos: [confirmado / corrigido]
- Datas com barra corrigidas para dd.mm.aaaa: [N]

Caminho do ODT final salvo na pasta de saída.
```

---

## Regras de formatação imutáveis

1. Fonte Arial em todo o documento, nunca alterar
2. 12pt no corpo do texto; 11pt em tabelas
3. Copiar formatação dos parágrafos adjacentes ao inserir texto
4. Nunca alterar conteúdo já existente além das correções do Passo 4
5. Nunca inventar dados não presentes no laudo ou nos autos
6. TRAVESSÃO ZERO em qualquer texto NOVO gerado (conclusão, respostas). Travessões já existentes no laudo original são preservados intactos.
7. Quesito sem resposta possível = em branco ou "Prejudicado.", sem texto algum
8. Usar gênero correto (autor/autora, o/a periciando/a) conforme o caso
9. Boilerplate (parágrafo 4) é obrigatório no Modelo A; NÃO usar no Modelo B

### Regra 10 — Considerações Finais sempre em nova página

A seção "Considerações Finais" SEMPRE deve começar em nova página.
O script aplica automaticamente `w:pageBreakBefore` no parágrafo do título.
Nunca deixar as Considerações Finais continuando na mesma página da seção anterior.

### Regra 10b — Espaçamento da conclusão (SEMPRE, SEMPRE, SEMPRE)

Entre cada bloco da Discussão/Conclusão inserir **obrigatoriamente** um parágrafo
vazio com estilo Body Text. O script `gerar_conclusao_odt.py` faz isso automaticamente.
Nunca comprimir os blocos em parágrafos consecutivos sem espaço.

### Regra 11 — Limpeza do cabeçalho

O script `gerar_conclusao_odt.py` remove automaticamente:
- `w:pBdr`: a linha preta horizontal que aparece no cabeçalho
- `w:numPr`: o número preto automático que aparece antes do texto do cabeçalho

Esses elementos são herdados do estilo Heading e devem ser removidos em todo laudo.

### Regra 12 — Respostas aos quesitos: objetivas, concisas e em itálico

Responder **somente o que foi perguntado**. Máximo de 1 a 2 frases por resposta.
O texto das respostas deve ser inserido **sempre em itálico** (o rótulo "Resposta:"
permanece no estilo normal). O script `gerar_conclusao_odt.py` aplica o itálico
automaticamente via `run_novo.font.italic = True`.

### Regra 13 — Data da página 1: verificar SEMPRE

A data da página 1 deve ser conferida e corrigida para a data atual em todo laudo
processado. O formato correto é: "Cidade, DD de mês de AAAA" (mês em minúsculas).
O script corrige automaticamente — se a data não for encontrada, alertar o Dr. Lino.

### Regra 14 — Espaçamento dos quesitos (formato obrigatório)

O espaçamento entre quesito e resposta deve ser **exatamente 1 (uma) linha em branco**,
nunca 2 (duas) ou mais. O template já contém as linhas em branco corretas; o script
**NÃO deve inserir nenhuma linha em branco adicional** ao preencher as respostas.

Formato correto:

[Texto do quesito]
[1 linha em branco — somente uma]
Resposta: [texto da resposta]
[1 linha em branco — somente uma]
[Próximo quesito]

**PROIBIDO:** adicionar 2 linhas em branco antes ou depois da "Resposta:".
O bloco `inserir_paragrafo_vazio_antes/apos` **não deve ser chamado** na função
`inserir_respostas` — o template original já tem o espaçamento correto.

### Regra 15 — Preservar numeração original dos quesitos

Nunca alterar a pontuação após o número do quesito. Preservar exatamente como está
no template (ponto ou vírgula após o número).

### Regra 16 — Verificação e confirmação do número de páginas

Após gerar o laudo, informar ao Dr. Lino o número de páginas detectado e pedir
confirmação antes de encerrar. Se Dr. Lino informar número diferente, corrigir
nas Considerações Finais e salvar novamente.

### Regra 17 — "Não se aplica" PROIBIDO — usar "Prejudicado"

Nunca usar a expressão "Não se aplica" em nenhuma resposta ou texto do laudo.
Sempre substituir por "Prejudicado."

### Regra 18 — "Dia"/"dia" ANTES de datas nos itens 1 e 2 dos Dados de interesse pericial

Nos itens 1 e 2 da seção "Dados de interesse pericial", usar "dia" antes de toda data
no formato dd.mm.aaaa. No item 3 (Consolidação), NÃO colocar "dia" antes da data.

### Regra 19 — "Bibliografia" e "Responsável por este laudo pericial" em novas páginas

Os itens "Bibliografia" e "Responsável por este laudo pericial" devem SEMPRE
iniciar em nova página, assim como "Considerações finais".

### Regra 20 — Ordem obrigatória da Conclusão (Modelo A) — VALIDADA junho/2026

A conclusão Modelo A segue 4 blocos lógicos, SEMPRE nessa ordem:

**BLOCO 1 — Histórico da doença (P1)**
Descreve o fato gerador (acidente ou doença profissional) com diagnóstico e CID.

**BLOCO 2 — Análise de funcionalidade e capacidade laborativa (P2 + P3)**
P2: tratamento realizado + sequela residual ("Embora tenha realizado...")
P3: repercussão no trabalho habitual ("Tal sequela gera maior dificuldade...")

**BLOCO 3 — Enquadramento legal (P4 + P5)**
P4: boilerplate "Com base nas informações obtidas..."
P5: enquadramento no Quadro 6 / Decreto 3048/99

**BLOCO 4 — Dados de interesse pericial (numerados)**
← 2 linhas em branco antes deste bloco, 1 linha entre todos os demais →
"Dados de interesse pericial:"
1. DID
2. Períodos de incapacidade (total/temporária → parcial/permanente)
3.Quanto a Consolidação (ABMLPM + "No caso em tela...")

Ordem completa dos 12 blocos do texto:
1. P1 (fato gerador)
2. P2 (tratamento + sequela)
3. P3 (repercussão laboral)
4. P4 (boilerplate)
5. P5 (Decreto 3048/99)
6. "Dados de interesse pericial:"  ← 2 blanks antes deste
7. Item 1 (DID)
8. Item 2 (incapacidade)
9. "3.Quanto a Consolidação:"
10. "- Segundo a ABMLPM..."
11. "Consolidação médico-legal da lesão..."  ← SEM hífen
12. "No caso em tela..."

NÃO alterar a sequência.
O script insere automaticamente 2 blanks antes de "Dados de interesse pericial:"
e 1 blank entre todos os demais blocos da conclusão.

### Regra 21 — Caixas dos quesitos do INSS/réu: espaço padrão entre os parênteses (SEMPRE)

Nos quesitos do réu (INSS), as caixas de marcação devem SEMPRE ter espaço padrão
entre os parênteses, tanto vazias quanto marcadas:
- Caixa vazia: `(   )` — no XML ODF: `( <text:s text:c="2"/>)`.
- Caixa marcada: `( X )` — espaço antes e depois do X. NUNCA `(X)` colado.

Como o script só preenche os "Resposta:", a marcação das caixas é feita por edição
do content.xml após gerar. Isolar a região dos quesitos do réu (de "Quesitos do réu"
até "Considerações finais") e trocar `(X)` por `( X )` e cada `( )` por
`( <text:s text:c="2"/>)`. Aplicar SOMENTE nos quesitos do INSS.
Confirmado pelo Dr. em 30/06/2026 (laudo Janice Maria Sausen).

### Regra 22 — Remover OBSERVAÇÕES PARA O PERITO antes de contar as folhas

A seção final "OBSERVAÇÕES PARA O PERITO" (notas internas do pré-laudo: pendências,
divergências de RG/endereço, CAT a confirmar etc.) NÃO vai no documento juntado aos
autos. SEMPRE removê-la ao finalizar. A ORDEM importa: PRIMEIRO cortar do parágrafo do
título `OBSERVAÇÕES PARA O PERITO:` até `</office:text>` e re-zipar cru; SÓ ENTÃO
recontar as páginas e atualizar o número em "Considerações finais" (a remoção costuma
reduzir uma folha). Confirmado pelo Dr. em 29/06 e reforçado em 30/06/2026.

### Regra 23 — Quesitos do réu (INSS) quando NÃO há incapacidade nem redução de capacidade

Quando a conclusão for do Modelo 3 ou 4 (capacidade plena / sem redução da capacidade
laborativa, com 4.1 marcado), formatar os quesitos do réu assim. Confirmado pelo Dr. em
01/07/2026 (laudo Junior Cezar Alves):

- **Q5** (a redução/incapacidade é temporária ou permanente): NÃO marcar nenhuma caixa
  (Temporária e Permanente ficam vazias). Resposta: "Prejudicado, não possui incapacidade
  ou redução da capacidade laborativa."
- **Q6** (data de início da redução/incapacidade): Resposta: "Prejudicado."
- **Q8** (potencial de reabilitação, com 2 caixas): puxar as duas opções para cima,
  COLADAS à pergunta (remover o parágrafo vazio entre a pergunta e as opções) e inserir
  embaixo "Resposta: Prejudicado." O template não tem campo "Resposta:" próprio no Q8;
  inserir manualmente no content.xml um parágrafo do rótulo "Resposta:" com o texto
  "Prejudicado." em itálico (span CONC_IT), após a 2ª opção e antes do 8.1.
- **Q8.1** (Sim/Não): NÃO marcar o "Sim". Deixar somente a resposta (ex.: "Não é caso
  para reabilitar; o autor mantém capacidade para a mesma atividade...").
- **Q10 e Q11** (cada um com caixas Não/Sim): puxar os parênteses das caixas para cima,
  COLADOS à pergunta (remover o parágrafo vazio entre a pergunta e as caixas).

Nesses casos, as ÚNICAS caixas marcadas do réu ficam **2.7** (acidente de trabalho) e
**4.1** (capacidade plena). Para "colar" as caixas à pergunta, remover no content.xml o
`<text:p .../>` vazio entre o parágrafo da pergunta e o parágrafo da primeira caixa.

### Respostas padrão adicionais confirmadas (laudo Nelson Heinert — junho/2026):

| Quesito | Resposta exata validada |
|---|---|
| Q6 Juízo (natureza da incapacidade) | "É Parcial e Permanente." |
| Q16 autor (PCD reconhecido pelo empregador) | "Sim." |

---

## AUXÍLIO-ACIDENTE — OS 4 TIPOS OBRIGATÓRIOS DE CONCLUSÃO

Quando o pedido for AUXÍLIO-ACIDENTE, a Discussão/Conclusão deve obrigatoriamente seguir UM destes 4 modelos. A diferença entre os modelos 1 e 2 é exclusivamente o enquadramento ou não no Anexo III do Decreto 3048/99.

### MODELO 1 — Redução de capacidade COM enquadramento no Anexo III (exemplo: LAUDO IZAIAS)
Após a frase de impacto e o parágrafo-ponte ("Com base nas informações obtidas na anamnese durante a expertise médico pericial, tomando-se por base a minudente análise retrospectiva documental e notadamente pelo exame físico geral e segmentar descrito no corpo do laudo técnico, como prerrogativa do Perito deste Juízo, este avaliador técnico de confiança do Magistrado conclui que:"):

> "O autor possui sequela que se enquadra tecnicamente no quadro [N] do Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

OBRIGATÓRIO: citar o número do quadro correto E transcrever a alínea exata logo abaixo. Exemplo (perda do polegar — quadro 5):
> "b) perda de segmento do primeiro quirodáctilo, desde que atingida a falange proximal; (Redação dada pelo Decreto nº 4.032, de 2001)"

Seguir com "Dados de interesse pericial:" — 1. DID estimada na data do acidente; 2. incapacidade total e temporária do acidente até a DCB; após a DCB, parcial e permanente que não impede o trabalho habitual, porém com maior dificuldade para algumas operações; 3. Consolidação: citar o conceito da ABMLPM ("Consolidação médico-legal da lesão, é quando, finalizados os tratamentos, esgotando-se as medidas terapêuticas atuais e disponíveis, não se vislumbrando evolução para melhora da lesão, configurando-se a sequela, um dano permanente.") e estimar a consolidação na DCB pelo critério da compatibilidade anátomo clínica.

### MODELO 2 — Redução de capacidade SEM enquadramento no Anexo III (exemplo: LAUDO ADEMAR)
Vai direto após a frase de impacto (sem o parágrafo-ponte). Texto exato:

> "Embora a existência de sequela que gera uma mínima redução da capacidade laborativa da parte autora, porém a mesma não possui enquadramento técnico no Anexo III do Decreto 3048/99(Relação de Situações que dão direito ao Auxílio Acidente)."

"Dados de interesse pericial" com consolidação curta: "3. Estima-se a consolidação do quadro na DCB em DD.MM.AAAA." Quesito sobre natureza da incapacidade: "É parcial(grau mínimo) e permanente."
Caso típico: amputação isolada do 3º, 4º ou 5º quirodáctilo (o quadro 5 exige dois quirodáctilos, ou o 1º/2º isoladamente).

### MODELO 3 — SEM perda de funcionalidade e SEM redução de capacidade (exemplo: LAUDO ELISA)
Antes da frase-ponte: "Foi realizado o devido tratamento e não restaram limitações funcionais." Frase-núcleo:

> "A autora não possui lesão ou sequela que possa ser classificada como incapacitante ou que reduza sua capacidade para o trabalho habitual, não havendo, assim, enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

Sem "Dados de interesse pericial". Quesitos sobre incapacidade: "Prejudicado".

### MODELO 4 — Perda de funcionalidade que NÃO gera redução de capacidade laborativa
Descrever a perda funcional objetivada ao exame (ex.: discreta limitação de amplitude, cicatriz, hipotrofia) e registrar que não interfere nas operações da atividade habitual. Frase-núcleo:

> "O autor possui perda de funcionalidade decorrente da lesão, porém tal perda não gera redução de sua capacidade para o trabalho habitual, não havendo, assim, enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

### ANEXO III DO DECRETO 3048/99 — RESUMO PARA ENQUADRAMENTO

- **Quadro 1 — Aparelho visual:** a) AV ≤0,2 no olho acidentado (após correção); b) AV ≤0,5 em ambos, quando ambos acidentados; c) AV ≤0,5 no acidentado quando o outro ≤0,5; d) paresia/paralisia de musculatura extrínseca; e) lesão bilateral de vias lacrimais (ou unilateral com fístula).
- **Quadro 2 — Aparelho auditivo (trauma acústico):** a) perda da audição no ouvido acidentado (>90 dB); b) redução grau médio+ (≥41 dB) em ambos, quando ambos acidentados; c) grau médio+ no acidentado quando o outro também reduzido. Audiometria aérea 500/1000/2000/3000 Hz, média aritmética: normal ≤25 dB; mínimo 26-40; médio 41-70; máximo 71-90; perda >90.
- **Quadro 3 — Fonação:** perturbação da palavra em grau médio ou máximo, comprovada objetivamente.
- **Quadro 4 — Prejuízo estético:** grau médio/máximo em crânio, face ou pescoço; perda de dentes com deformação de arcada que impeça prótese. Perda anatômica/redução de movimentos NÃO é prejuízo estético.
- **Quadro 5 — Perdas de segmentos de membros:** a) ao nível ou acima do carpo; b) 1º quirodáctilo, atingida a falange proximal; c) DOIS quirodáctilos, atingida a falange proximal em pelo menos um; d) 2º quirodáctilo, atingida a falange proximal; e) 3+ falanges de 3+ quirodáctilos; f) ao nível ou acima do tarso; g) 1º pododáctilo, atingida a falange proximal; h) dois pododáctilos, atingida a falange proximal em ambos; i) 3+ falanges de 3+ pododáctilos. NOTA: perda parcial de parte ÓSSEA equivale à perda do segmento; perda só de partes moles NÃO enquadra. ATENÇÃO: amputação isolada do 3º, 4º ou 5º quirodáctilo NÃO enquadra → usar MODELO 2.
- **Quadro 6 — Alterações articulares:** a) mandíbula grau médio+; b) coluna cervical grau MÁXIMO; c) lombo-sacra grau MÁXIMO; d) ombro ou cotovelo grau médio+; e) prono-supinação do antebraço grau médio+; f) 1º e/ou 2º quirodáctilo grau MÁXIMO (articulações MCF e IF atingidas); g) coxofemoral/joelho/tibiotársica grau médio+. Graus: máximo = redução >2/3 da amplitude normal; médio = >1/3 até 2/3; mínimo = até 1/3. NOTA 2: redução de movimentos de cotovelo, prono-supinação, punho, joelho e tibiotársica secundária a fratura de osso longo consolidada em posição viciosa com desvio de eixo também enquadra.
- **Quadro 7 — Encurtamento de MI:** mais de 4 cm.
- **Quadro 8 — Redução de força/capacidade funcional dos membros:** grau SOFRÍVEL (grau 3 = 50%, movimento completo contra gravidade sem resistência) ou inferior — a) mão/punho/antebraço/MS; b) 1º quirodáctilo; c) pé/perna/MI. Só comprometimento muscular ou neurológico; não se aplica a lesões articulares ou perdas anatômicas (quadros próprios). Limitação em grau leve NÃO enquadra.
- **Quadro 9 — Outros:** a) segmentectomia pulmonar com redução respiratória grau médio+, correlacionada à atividade laborativa; b) perda de segmento do aparelho digestivo com repercussão nutricional/estado geral.

### CORREÇÕES CONFIRMADAS PELO DR. LINO (12.06.2026)
1. Citar SEMPRE o quadro e a alínea corretos do Anexo III oficial (laudos antigos citavam "quadro 6" para perda de segmento de dedo; o correto é o quadro 5 — Perdas de segmentos de membros).
2. O LAUDO VALDIR contém erro ("se enquadra no quadro 6") — amputação isolada do 5º quirodáctilo NÃO se enquadra no Anexo III; o exemplo correto do modelo 2 é o LAUDO ADEMAR.

### CONVENÇÃO DE COMANDO
Dr. Lino pode indicar o modelo diretamente no comando (ex.: "conclusao1 modelo 2") — usar o modelo indicado sem questionar. No modelo 1, mesmo com modelo indicado, identificar e citar SEMPRE o quadro e a alínea corretos do Anexo III conforme a lesão. Se o modelo não for indicado, classificar pelo exame físico/autos e informar qual modelo foi aplicado; em dúvida entre dois modelos, perguntar antes.
