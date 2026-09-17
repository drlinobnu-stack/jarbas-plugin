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

## REGRA ABSOLUTA E GLOBAL: LÉXICO PROIBIDO (respostas e conclusão)

> **Não usar "objetiva-se" nem "objetivar"** (nem as conjugações objetivada, objetivado, objetivou, objetivam...). Trocar SEMPRE por **"observa-se" / "observar"** (observada, observado, observou). O adjetivo/substantivo "objetivo/objetiva" (ex.: "resposta objetiva", "o objetivo da perícia") continua permitido. O `gerar_conclusao_odt.py` já faz a troca automática nas RESPOSTAS (função `objetivar_para_observar`, dentro de `proc_texto`); na conclusão redigida à mão, evitar o termo. Confirmado pelo Dr. em 10/07/2026.
>
> **Não usar "residual"** para qualificar incapacidade ou sequela quando NÃO há sequela nem incapacidade. Tecnicamente, "residual" afirma que EXISTE uma sequela/incapacidade, porém menor que 10% da função do segmento avaliado. Só cabe "residual" quando de fato há essa pequena perda comprovada; nos casos SEM qualquer sequela (Modelos 3, 4 e 5), nunca escrever "sequela residual" nem "incapacidade residual" — usar "sem sequela", "sem redução da capacidade laborativa" ou "restituição integral", conforme o caso. Confirmado pelo Dr. em 10/07/2026.
>
> **Grafia "Estresse" (nunca "Estress"):** nos testes de estabilidade do joelho, escrever SEMPRE "Estresse em varo" / "Estresse em valgo" (com o "e" final), nunca "Estress". Vale para qualquer laudo/exame que passe pelas mãos de Claude: ao encontrar "Estress em varo/valgo" no exame físico digitado pelo Dr., corrigir para "Estresse em varo/valgo". Confirmado pelo Dr. em 03/08/2026 (laudo Leomar). O `gerar_conclusao_odt.py` já faz a troca (função `normalizar_termos`), e o revisor-laudo aponta a grafia "Estress" como correção obrigatória, não observação menor.

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

6. **Anexos ESCANEADOS: varredura obrigatória (nunca pular).** Boa parte dos autos
   (prontuários hospitalares, AIH, termos de consentimento, agendamentos de cirurgia,
   fichas de SAMU e de pronto-socorro) vem como IMAGEM, sem camada de texto. Esse
   material não aparece em nenhuma busca por palavra e é justamente onde costuma estar
   o documento que decide o caso. Procedimento:

   a) Listar as páginas do PDF que têm menos de ~120 caracteres de texto extraível
      (`page.get_text()` do PyMuPDF): são as escaneadas.
   b) Renderizar essas páginas em FOLHAS DE CONTATO 3x3, a ~70 dpi, com o número da
      folha escrito em cada miniatura, e ler por visão. É rápido e cobre dezenas de
      páginas em poucas leituras.
   c) Reabrir em ALTA resolução (>= 250 dpi, recortando a região de interesse) somente
      as folhas que interessarem, para transcrever datas e frases com exatidão.
   d) Nunca transcrever de memória nem "por dedução" do que a miniatura sugere: a frase
      citada no laudo tem de vir da leitura em alta resolução.

   Priorizar os documentos com data IMEDIATAMENTE ANTERIOR ao fato discutido
   (AIH, agendamento de cirurgia, termo de consentimento, encaminhamento, receita):
   são eles que estabelecem o estado clínico prévio.

7. **QUESITOS SUPERVENIENTES: conferir o processo NO DIA da redação (regra do Dr., 28.08.2026).**
   O PDF dos autos que instruiu o pré-laudo foi baixado semanas antes; nesse intervalo as partes
   podem ter protocolado quesitos. Antes de escrever a seção 8, abrir o processo no eproc e olhar
   os EVENTOS, procurando **APRESENTAÇÃO DE QUESITOS** (ou petição com quesitos) de qualquer das
   partes com data posterior à do PDF baixado. Quesitos do autor vêm por ADVOGADO (com OAB); os do
   INSS, por procurador federal (em regra o INSS só peticiona honorários e não apresenta quesitos).

   Ao escrever que não há quesitos, **datar a afirmação e nomear o evento**: "Consultados os autos
   eletrônicos até o evento N, de DD.MM.AAAA, não foram localizados quesitos apresentados pela parte
   autora." Isso cria uma âncora verificável, que a etapa de entrega vai conferir contra o último
   evento real ([[entregar-laudo-eproc]], [[sisperjud]]) — e é o que impede a peça de ser protocolada
   negando quesitos que já estão nos autos.

   Caso que originou a regra: [[caso-jean-rafael-brauvers-quesitos-autor-tardios]] — laudo pronto
   afirmando não haver quesitos do autor (autos consultados até o evento 27, de 02.07.2026), com 15
   quesitos protocolados no evento 28, de 12.08.2026, dirigidos contra a conclusão. Respondê-los
   depois custou 5 folhas a mais e uma recontagem da seção 9.

8. **Ação de CONVERSÃO ou reativação: o laudo de OUTRO processo vem encartado.** Nesses autos o
   PDF costuma trazer o laudo do perito do processo anterior, com os quesitos daquela perícia.
   Os quesitos a responder são os do processo ATUAL, transcritos no pré-laudo pela secretária; os
   do laudo antigo já foram respondidos lá e não entram. Só acrescentar dos autos o quesito que
   for inequivocamente do processo atual. Ao delegar a leitura dos autos a um subagente, exigir a
   PROVENIÊNCIA de cada bloco de quesitos (evento, folha e processo) antes de aceitar o relatório.
   Caso que originou a regra: Marlene Sandoval, Rio do Sul, 07.08.2026 (o subagente devolveu 6
   quesitos do juízo e 16 do réu, todos do laudo antigo).

9. **Perícias administrativas do INSS: ler a DID, a DII e o CID de cada benefício ANTES de firmar
   nexo com o acidente.** Uma conclusão ditada como "sequela pós acidente" pode conflitar com a
   cronologia documentada: no caso Luiz Eduardo Lopes (21.08.2026) a perda visual tinha DID 2018 e
   DII 11.10.2019, anteriores ao acidente de 2021. Se a origem da sequela for anterior ao acidente,
   tratar como pré-existente e só admitir concausa com agravamento demonstrável (ver a Regra 25),
   sempre com nota do componente pré-existente. Divergência entre a instrução recebida e os autos é
   ponto de PARAR e confirmar com o Dr., nunca de acomodar o texto.

10. **Formulários de duas colunas do INSS (laudo SABI, comunicação de decisão, CAT, espelho de
   benefício) só se afirmam depois de ler a PÁGINA COMO IMAGEM.** A extração de texto embaralha
   rótulo e valor e produz afirmação falsa com cara de citação exata (no caso Jean Brauvers,
   27.08.2026, o "NÃO" atribuído ao campo "Auxílio Acidente" era da linha "Sug. de Apos. por
   Invalidez"). Antes de citar qualquer campo desses formulários na Discussão ou numa resposta,
   renderizar a página e ler o par rótulo-valor na imagem; se a imagem não resolver, citar o que é
   verificável por outra via (Declaração de Benefícios, espécie e DCB) em vez do campo.

### Passo 4 — VERIFICAÇÕES E CORREÇÕES AUTOMÁTICAS OBRIGATÓRIAS

Executar todas antes de redigir a conclusão. Registrar cada correção.

#### 4.1 — Data da página 1

1. Localizar a data na página 1 (formato: "Cidade, DD de Mês de AAAA", mês em MAIÚSCULA, por extenso).
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

#### 4.2b — Remover a tabela de Exames (4.2) quando NÃO há exames nos autos (automático)

Se não houver exames complementares juntados aos autos, a subseção "4.2. Exames
complementares:" não pode ficar com a tabela vazia (só os cabeçalhos DATA/EXAME/Nº
Folha/CONCLUSÃO). O `gerar_conclusao_odt.py` remove sozinho o título e a tabela vazia e
renumera as subseções seguintes do item 4 (4.3 Benefícios vira 4.2), na função
`remover_tabela_exames_vazia`. A renumeração só age ANTES da seção 5, portanto não toca
nas alternativas 4.1/4.2/4.3/4.4 do Quesito 4 do réu (seção 8.3). Havendo exame, a
tabela é mantida. Regra do Dr., confirmar no revisor. Ver
[[feedback_sem_exames_apagar_tabela]].

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

#### 4.6 — COBERTURA: toda condição com valoração na seção 4 foi examinada e endereçada?

Listar as patologias e sequelas que os documentos da seção 4 trazem COM valoração ou grau
(atestado com "redução de 50% do pé", laudo de perícia anterior com percentual, benefício de
outra lesão) e conferir, uma a uma, se (a) o segmento foi examinado na seção 6 e (b) a condição
foi tratada na conclusão ou nos quesitos. Segmento documentado com sequela e NÃO examinado: não
inventar achado; redigir a conclusão só sobre o que foi examinado e SINALIZAR ao Dr. antes de
fechar, para ele decidir se complementa o exame. Caso Jefferson Rudolf (31.07.2026): atestado de
50% do pé esquerdo na 4.1 e exame só de ombro e punho. O revisor-laudo confere o mesmo ponto.

#### 4.7 — Laudo vindo de .doc (fora do template do JARBAS): checklist próprio

Converter para ODT antes de qualquer edição e conferir: IMC (o campo costuma vir "1" ou vazio),
dados bancários atuais (Ag. 0411, não 3954), contagem de folhas ("xxx"), e os campos "Resposta:"
vazios com variação de espaçamento (o regex de preenchimento tolera "Resposta:" com e sem espaço).
Ver também a Regra 30 (cabeçalho). Caso Luiz Eduardo Lopes, 21.08.2026.

#### 4.8 — Integridade do cabeçalho em ODT que foi reaberto no Office

Todo laudo que passou por abrir/salvar no OpenOffice ou no Word antes de chegar aqui pode ter
perdido o logo mantendo o frame vazio. Antes de finalizar, conferir no styles.xml: `<draw:image>`
com `xlink:href` não vazio, o PNG presente no zip (Pictures/) e a entrada no manifest. O
`gerar_conclusao_odt.py` roda o `restaurar_logo.py` no fim, mas o diagnóstico manual vale quando
o Dr. disser "o cabeçalho sumiu". Regra 30 traz o que sobrevive e o que não sobrevive ao editor.

### Passo 5 — Redigir a Discussão e Conclusão

Redigir o texto completo da seção "Discussão / Conclusão" seguindo **exatamente**
o estilo do Dr. Francisco Lino, conforme os laudos modelo.

> **SISPERJUD: a seção chama-se "Observações", não "Discussão / Conclusão".** Regra do
> Dr. 24.08.2026 (pauta Guabiruba). Nas comarcas que entregam por SISPERJUD (Gaspar,
> Guabiruba, Rio do Sul, Timbó e outras que a nomeação indicar), a conclusão formal
> (enquadramento, DID, DCB, consolidação) é lançada nos campos estruturados da
> plataforma; no ODT o item narrativo é intitulado **"Observações"**. Portanto: (a) o
> título do item vira "N. Observações:" em vez de "N. Discussão / Conclusão:"; e (b) as
> referências nas respostas aos quesitos passam de "vide item Discussão e Conclusão
> deste laudo" para **"vide item Observações deste laudo"**. O texto (o raciocínio
> médico) permanece o mesmo, só muda o rótulo. No eproc (não SISPERJUD) mantém-se
> "Discussão / Conclusão". Ainda NÃO automatizado nos geradores.

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
   Parágrafo a: "3. Quanto à Consolidação:"
   (Nota: LEVA CRASE: "Quanto à" (teste: "Quanto ao diagnóstico" -> "Quanto à
   consolidação"). Espaço após o "3.", igual aos itens 1 e 2. Corrigido pelo Dr.
   em 16/07/2026, laudo George Lucio Fortes; o formato antigo "3.Quanto a" sem
   crase e colado estava errado.)
   Parágrafo b: "- Segundo a ABMLPM na descrição de Conceitos Médicos Legais da Tabela
   Brasileira para Apuração do Dano corporal, temos que:"
   (ATENÇÃO: o parágrafo começa com "- Segundo", com hífen e espaço antes de "Segundo")
   Parágrafo c: "Consolidação médico-legal da lesão, é quando, finalizados os
   tratamentos, esgotando-se as medidas terapêuticas atuais e disponíveis, não se
   vislumbrando evolução para melhora da lesão, configurando-se a sequela, um dano
   permanente."
   (ATENÇÃO: SEM hífen antes de "Consolidação" — diferente do parágrafo b que TEM "- Segundo")
   Parágrafo d: "No caso em tela, estima-se a consolidação do quadro na DCB, em
   [data], pelo critério da compatibilidade anatomoclínica."
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
  um período de mais [prazo] de incapacidade laborativa."
  (REGRA Dr. 16.07.2026: na incapacidade total e temporária com prazo definido NÃO há
  reavaliação pericial; NUNCA escrever "para reavaliação"/"nova avaliação"/"nova perícia".)

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

## MODELO C — Lesão NÃO CONSOLIDADA (sem valoração da sequela)

Usar quando o periciando ainda está em tratamento (ortopédico, fisioterápico), tem cirurgia
indicada e não realizada, ou laudos e imagens recentes sem alta. Sem consolidação médico-legal
não há sequela definitiva a valorar; a conclusão descreve a lesão e documenta a impossibilidade de
quantificar, remetendo a nova perícia após a alta. Definido pelo Dr. em 15.07.2026 (Divonsir
Soares dos Santos, luxação recidivante do ombro esquerdo, cirurgia indicada pendente).

Gatilho: tratamento em curso OU cirurgia indicada não realizada OU documentos recentes sem alta.

**Parte 1, descrição da lesão (redação do perito):** mecanismo e data do acidente; diagnóstico
com CID; síntese do exame físico; síntese dos exames de imagem; situação do tratamento (ex.:
"cirurgia indicada ainda não realizada").

**Parte 2, texto padrão FIXO do Dr. (reproduzir literalmente):**

> "Considerando-se que não houve 'consolidação médico legal das lesões traumáticas', ou seja, o
> periciado não encerrou o tratamento médico (ortopédico) e fisioterápico, apresenta-se como
> impossível a quantificação de eventual grau de sequela pós-traumática permanente."

> "Obs: Quando ocorrer 'alta médica definitiva', existe a necessidade de comprovação documental
> nos autos para a realização de NOVA PERÍCIA MÉDICA JUDICIAL."

**Duas variantes, decididas pelo exame:**

- **C1, com redução subsistindo** (caso Ana Sueli, memória conclusao-auxilio-acidente-sem-consolidacao):
  há limitação ao exame, mas o quadro segue em tratamento. Descrever a limitação atual e fechar
  com o texto padrão. Não enquadrar no Anexo III nem no art. 86: ambos pressupõem consolidação.
- **C2, sem redução alguma e doença ativa** (caso Jefferson Rudolf, 31.07.2026): exame inteiramente
  normal, doença em atividade, possível cirurgia. Não é Modelo 3 (que pressupõe tratamento
  concluído sem sequela) nem Modelo 5 (que é consolidado). Estrutura validada: P1 diagnóstico; P2
  segmentos sem doença (variação anatômica etc.); P3 etiologia e nexo; P4 exame atual sem
  limitação; P5 boilerplate; P6 não consolidação; P7 o art. 86 exige consolidação COM sequela
  redutora, ausentes ambas, sem Anexo III, e recomendação de reavaliação após a consolidação.

**Dados de interesse pericial:** 1. DID; 2. "sem incapacidade nem afastamento" (C2) ou o período
documentado (C1); 3. Consolidação: conceito da ABMLPM e a afirmação de que o quadro NÃO está
consolidado.

**Quesitos:** grau, valoração, DIIP e consolidação ficam prejudicados, com a frase que explica:
"consolidadas?" = "Não. O quadro não se encontra consolidado."; consolidação x DCB = "Prejudicado.
O quadro não se encontra consolidado."; valoração = "Prejudicado. A lesão não está consolidada,
não sendo possível quantificar a sequela." Nunca "Prejudicado." solto. IMC e revisor como sempre.

---

## MODELO D — Há dano, mas NÃO há nexo acidentário (causa pré-existente ou patológica)

Usar quando existe sequela ao exame, mas a hipótese mais provável é que ela decorra de condição
pré-existente e constitucional (tumor ósseo, doença metabólica, degeneração documentada) ou do seu
tratamento cirúrgico, e não do acidente, que serviu apenas de fator desencadeante. Caso que
originou o modelo: Daniela Klabunde, 21.08.2026 (fratura patológica da falange proximal do 5º dedo
sobre encondroma registrado desde 2004, ressecado com curetagem e enxerto de ilíaco).

**Estrutura:** reconhecer a sequela ao exame (com goniometria, distância polpa-palma e comparação
com o contralateral, nunca só "grau leve"); documentar a pré-existência com data e teor do
documento; explicar o mecanismo (fratura patológica em osso enfraquecido, acidente como mero
desencadeante); afastar o nexo com a sequela. NÃO usar o boilerplate do Decreto 3048/99 nem o
quadro 6. Literatura REAL em nota de rodapé (para encondroma, validadas: Zyluk 2021 PMID 34734563;
Ramos-Pascua 2018 PMID 29551341; Zheng 2014 PMID 25106766; Çapkin 2020 PMID 32373401; Hung 2015
PMID 25810024; Ipponi 2024 PMID 39781633). Quando houver dois ou mais acidentes e só a CAT de um
constar, sinalizar a lacuna documental.

**Blindagem obrigatória, escrita na própria conclusão** (os três ataques são previsíveis, ver o
Advogado do Diabo do caso Klabunde):

1. Distinguir por escrito o nexo do AFASTAMENTO temporário (que existiu: auxílio-doença
   acidentário, espécie 91) do nexo da SEQUELA definitiva, único objeto do art. 86, que se afasta.
2. Enfrentar a concausa: o trauma foi concausa apenas do evento agudo já resolvido; a causa
   determinante da limitação residual está na doença de base e no ato cirúrgico. Não chamar o
   acidente de "fator desencadeante" sem essa explicação, porque a expressão é definição de
   concausa e atrai o art. 86.
3. Resolver a aparente contradição entre admitir sequela permanente com repercussão no trabalho e
   negar o benefício: o benefício exige nexo da sequela com o acidente, não só a existência dela.

A atribuição de causa é probabilística: assumir a incerteza e blindá-la com literatura pertinente é
mais defensável do que afirmá-la como certeza. Se o Dr. optar por CONCAUSA em vez de ausência de
nexo, é decisão dele: apontar as duas saídas e entregar a que ele indicar.

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

| Tratamento em curso, cirurgia indicada, sem alta (auxílio-acidente) | Modelo C (não consolidada) |
| Sequela presente, mas causa pré-existente ou patológica documentada | Modelo D (dano sem nexo) |

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
- "Mais detalhes, vide item Discussão e Conclusão deste laudo." é resposta válida e preferível
  quando o quesito pede o que já está na conclusão
- "Vide item 3 do laudo." para questões de profissiografia
- "Prejudicado." para quesitos sobre incapacidade total permanente (que não existe)
- "Não é caso para reabilitar, pode fazer a mesma atividade que desenvolvia na época
  do acidente, porém com maior dificuldade para algumas operações." para quesitos 8/8.1/8.2
- "Gera limitação para atividades pontuais." para quesito sobre trabalho doméstico (Q15)
- "A limitação de funcionalidade claramente detectada nas manobras propedêuticas do
  exame pericial é que ampara tal divergência. Mais detalhes, vide item Discussão e
  Conclusão deste laudo." para quesito de divergência com laudo administrativo (Q16)

**Quesitos específicos com resposta padrão validada:**

| Quesito | Resposta padrão |
|---|---|
| Q1 autora (ciência art. 473 CPC) | "Sim. Este perito tem ciência de tal disposição e todas as respostas estão fundamentadas nos achados periciais." |
| Q5 autora (concordar com legislação) | "Não é objetivo deste laudo concordar ou discordar da legislação." |
| Q juízo nexo (h) — "decorrente de doença profissional/do trabalho? nexo com a última atividade?" | Em caso de ACIDENTE (auxílio-acidente): "Há nexo causal das lesões citadas no item 3 do laudo com o acidente de trabalho ocorrido. Mais detalhes, vide item Discussão e Conclusão deste laudo." Enquadrar o nexo como LESÕES (item 3) ↔ ACIDENTE, não patologia ↔ atividade. NÃO nomear a atividade nem citar CAT/benefícios na resposta (a fundamentação vai na Discussão). Ver [[feedback-quesito-nexo-lesoes-acidente]] |
| Q réu 1 (diagnóstico/CID) | Repetir P1 + P2 da conclusão na íntegra |
| Q réu 2 (causa) | Marcar 2.7 com (X); justificativa: mais detalhes, vide item Discussão e Conclusão deste laudo |
| Q réu 5 (a redução/incapacidade é temporária ou permanente?) | Se HÁ redução permanente (auxílio-acidente com sequela): marcar "Permanente". Se RESTITUIÇÃO INTEGRAL / capacidade plena (4.1 marcada, sem sequela): NÃO marcar nenhuma caixa e responder "Prejudicado. A [autora/o autor] não apresentou ao atual exame pericial, incapacidade laborativa ou redução de sua capacidade para o trabalho que tinha na época do acidente." NÃO marcar "Temporária" só porque houve incapacidade temporária no passado (já cessada): o quesito pergunta pela natureza de uma redução ATUAL, que na restituição integral não existe. Regra do Dr. 06.08.2026 (laudo Josiane). Ver [[feedback-reu-q5-temporaria-permanente-prejudicado]] |
| Q réu 6 (data início redução) | "Na consolidação em [data], pelo critério da compatibilidade anatomoclínica." |
| Q réu 8/8.1/8.2 (reabilitação) | COM sequela: "Não é caso para reabilitar, pode fazer a mesma atividade que desenvolvia na época do acidente, porém com maior dificuldade para algumas operações." Restituição integral / sem incapacidade: "Prejudicado." (o quesito 8 principal é um "gateway" que às vezes NÃO traz linha "Resposta:" própria no template, só as caixas: nesse caso o quesito sai SEM resposta se não for inserida uma; conferir e responder mesmo assim). |
| Q réu 9/10/11 (incap. total permanente) | "Prejudicado." |
| Q réu 15 (trabalho doméstico) | "Gera limitação para atividades pontuais." |

**Por tipo de quesito geral:**
| Tipo | Como responder |
|------|---------------|
| Quesito pede o que já está na conclusão | "Mais detalhes, vide item Discussão e Conclusão deste laudo." |
| Quesito sobre profissiografia | "Sim, vide item 3 do laudo." |
| Incapacidade para a profissão (é incapacitante? total/parcial?) | Auxílio-acidente é incapacidade PARCIAL e permanente. Responder SEMPRE: "Há redução parcial e permanente da capacidade para o trabalho habitual, que não impede o seu exercício, ainda que com maior dificuldade." Ir direto, sem "não incapacita"; referência é o TRABALHO HABITUAL, não a profissão atual. Ver [[feedback-incapacidade-parcial-permanente-resposta]] |
| Permanente ou temporária | "Permanente (X)." |
| Incapacita para toda atividade | "Prejudicado." |
| Necessita assistência permanente | "Prejudicado." |
| Quesito sobre reabilitação profissional | "Não é caso para reabilitar..." |
| **Concordar/discordar de legislação** | "Não é objetivo deste laudo concordar ou discordar da legislação." |
| **Abonar/desabonar documento, laudo ou atestado de terceiro** (ex.: "este Perito DESABONA o laudo?", "é possível acolher o diagnóstico apontado por seu colega?") | Não cabe ao perito abonar/desabonar peças das partes. Responder: "Prejudicado, não é objetivo desta perícia abonar ou desabonar documentos que as partes trazem aos autos, mas avaliar pericialmente o autor com a devida anamnese e exame físico pericial presencial, além de avaliar os documentos trazidos aos autos e emitir uma conclusão pericial de forma autônoma e imparcial para ajudar ao magistrado." Se o quesito invocar Parecer/Resolução do CFM sobre o Médico do Trabalho poder discordar de atestado, apontar que o dispositivo se refere ao **Médico do Trabalho e não ao Médico Perito Judicial**, de modo que o enfoque do quesito está errado. Regra do Dr. 24.08.2026 (laudo Rogerio Laguna). |
| **Esforço físico excessivo** | "Ninguém está apto para atividades com esforços físicos excessivos e constantes, para balizar tais situações existe a NR 17 que versa sobre ergonomia e suas implicações no trabalho." |
| **Igualdade no mercado de trabalho** | "Prejudicado, não é objetivo desta perícia tal avaliação." |
| **Adaptação ergonômica** | "Prejudicado, não é objetivo desta perícia tal avaliação." |
| **Performance esportiva (atleta profissional)** | "A performance esportiva não é objeto desta perícia." |
| **Paridade competitiva no meio esportivo** | "Prejudicado, não é objetivo desta perícia tal avaliação." |

**Quesitos de ATLETA PROFISSIONAL (validado no laudo Johann Buetes Arndt, 29/07/2026):** quando a profissão habitual é atividade física de alto rendimento, separar o que é medicina-pericial (limitação funcional objetiva ao exame) do que é desempenho ou competitividade esportiva (fora do escopo). Perguntas sobre performance, paridade com atleta sem histórico de lesão e capacidade competitiva respondem-se como "não é objeto/objetivo desta perícia"; as exigências físicas específicas (arrancadas, giros, saltos, desaceleração, contato) respondem-se pela presença ou ausência de limitação funcional ao exame. IMPORTANTE: para o atleta profissional, a partida ou o treino É a atividade laboral, então o acidente esportivo ocorrido nesse contexto é acidente no exercício do trabalho e marca-se a caixa 2.7 do réu (acidente de trabalho).

**Datas dentro das respostas (regra única):** escrever SEMPRE "no dia DD.MM.AAAA", "emitido no dia DD.MM.AAAA" ou "datado do dia DD.MM.AAAA". O `gerar_conclusao_odt.py` insere "dia" antes de datas dd.mm.aaaa nas respostas; desde 27.08.2026 ele respeita as preposições que já regem a data ("de", "em", "desde", "até", "entre ... e", "na data de"), mas a forma segura continua sendo escrever o "dia" por extenso, porque cada exceção nova só entra na lista depois de estragar um laudo (foram três: "em dia", "de dia" e "data de dia"). Datas de exame, de acidente, de DCB e de documento: todas.

**Subtipo: comarca SISPERJUD com quesitação do juízo NÃO transcrita e INSS citado só se o laudo for favorável** (Guabiruba, Ivanor Seidler, 21.08.2026). O ODT do pré-laudo traz os quesitos do juízo com a nota "obter no sistema" e a seção 8.3 do réu como "Não localizados nos autos". Nesse caso: manter no ODT a resposta ao quesito do juízo apontando para a quesitação do sistema, deixar a seção do réu como está e NÃO passar `marcar_caixas_reu` (as caixas não existem no template; o script só reporta "não localizadas"). A Discussão e os Dados de interesse pericial vão normalmente; a quesitação numerada é respondida na transcrição pela skill /sisperjud.

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
     "quesitos_reu":   [{"numero": "1", "resposta": "..."}],
     "marcar_caixas_reu": ["2.7", "4.2", "Permanente"]
   }
   ```
   Quesito sem resposta possível: deixar `"resposta": ""` (fica em branco) ou
   `"resposta": "Prejudicado."`. NUNCA "Não se aplica".

   **Campo `marcar_caixas_reu`** (opcional): lista dos rótulos das caixas do réu a
   marcar com `( X )`. O script `gerar_conclusao_odt.py` (função `marcar_caixas_reu`)
   localiza o PARÁGRAFO pelo texto (tolera `<text:soft-page-break/>` e spans), marca a
   PRIMEIRA caixa VAZIA daquele parágrafo (robusto a `( )`, `()` e `( <text:s/>)`, sem
   confundir com parênteses de texto) e padroniza as demais vazias como `(   )`.
   Auxílio-acidente COM redução: `["2.7","4.2","Permanente"]`. Capacidade plena
   (Modelo 3): `["2.7","4.1"]`. Templates sem caixas (quesitos abertos): omitir o campo.
   Ainda assim, conferir as caixas marcadas no revisor antes de entregar.

3. Rodar o gerador ODT (trabalha sobre uma cópia, não altera o original):
   ```bash
   python3 ~/.claude/scripts/gerar_conclusao_odt.py \
     --laudo  "LAUDO_ENTRADA.odt" \
     --conclusao  conclusao-texto.txt \
     --respostas  quesitos-respostas.json \
     --saida  "CAMINHO_DE_SAIDA.odt" \
     --autos  "NUMERO-DOS-AUTOS"
   ```

**Caminho canônico: SEMPRE `~/.claude/scripts/gerar_conclusao_odt.py`.** A cópia que vive dentro do plugin (`~/.claude/plugins/cache/jarbas-lino/jarbas/1.0.0/scripts/`) NÃO é autossuficiente: importa `lino_redacao.py` e `fix_header_logo.py`, que só existem em `~/.claude/scripts/`, e quebra com ModuleNotFoundError (caso Dubiela, 04.08.2026). O `propagar_jarbas.sh` copia os módulos irmãos junto, mas o comando documentado é o de `~/.claude/scripts`.

O script `gerar_conclusao_odt.py`:
- Insere os blocos da conclusão entre "Discussão / Conclusão:" e "Quesitos:",
  com 1 linha em branco entre blocos e 2 antes de "Dados de interesse pericial:".
- Preenche cada "Resposta:" na ordem, em itálico (estilo CONC_IT).
- Em texto NOVO: remove travessões, troca "Não se aplica" por "Prejudicado",
  põe "dia"/"Dia" antes de datas dd.mm.aaaa.
- Corrige a data da página 1 para hoje (se diferente).
- Remove sozinho a seção "OBSERVAÇÕES PARA O PERITO" ANTES de contar as folhas (automático desde
  05.09.2026, depois de duas reincidências da remoção manual esquecida; ver a Regra 22).
- Converte para texto as células de data TIPADAS das tabelas (`office:value-type="date"`), que o
  editor cria quando o Dr. digita uma data numa célula: sem isso o LibreOffice reconstrói "13/03/25"
  a partir do `office:date-value` mesmo com o texto trocado (caso Viviane, 24.08.2026).
- Substitui "xxx (xxx)" das Considerações finais pela contagem real de folhas
  (converte o ODT para PDF via LibreOffice e conta as páginas; não usa poppler).
- Re-zipa o ODT cru (mimetype primeiro) preservando o cabeçalho/logo e todo o
  resto. NUNCA reconverte o ODT pelo LibreOffice (isso quebraria o cabeçalho).
- Ao final, DEPOIS de restaurar o logo, roda a HIGIENIZAÇÃO automática (a skill
  `/limpar-laudo`, via `limpar_laudo.limpar_arquivo`): remove caracteres
  invisíveis (zero-width, joiners, marcas de direção, caracteres de "tag") e os
  metadados de origem do ODT (gerador, autor do template, data de criação antiga,
  tempo e ciclos de edição), e limpa os metadados das imagens sem recomprimir
  (logo preservado). NÃO altera o texto (respeita "nunca inventar") e é defensiva:
  se falhar, não quebra a geração (o log traz "limpeza: ..."). Por isso o laudo já
  sai higienizado; não é preciso rodar `/limpar-laudo` à mão sobre o que passou
  pelo gerador. Confirmado pelo Dr. em 22.08.2026.

As quebras de página antes de Considerações finais, Bibliografia e Responsável já
vêm do template do JARBAS e são preservadas.

### Passo 8 — IMC e REVISÃO FINAL OBRIGATÓRIA (agente revisor-laudo)

**IMC:** o laudo de conclusão já vem com o exame físico preenchido. A partir do peso e
da altura do exame, calcule o IMC (peso dividido pela altura ao quadrado), preencha o
campo "IMC:" com o valor e, na lista de classificação, mantenha SOMENTE a faixa em que
o periciado se enquadra, apagando as demais. Nunca pode sobrar mais de uma faixa.
A faixa que fica (abaixo da tabela) deve estar em **Arial 10, preta, e COLADA à tabela**
de peso/altura/IMC (sem o parágrafo vazio entre a tabela e a faixa). Confirmado pelo Dr.
em 02/07/2026. O script `gerar_conclusao_odt.py` já faz isso na função `colar_faixa_imc`
(cria o estilo IMCFX e remove o vazio); em edição manual do XML, remover o `<text:p .../>`
vazio entre `</table:table>` e a faixa e reestilizar a faixa para Arial 10pt.

**Revisão final:** antes de entregar, rode SEMPRE o subagente `revisor-laudo` (ferramenta
Task/Agent) sobre o ODT gerado. Ele renderiza o PDF, percorre todas as páginas e confere
a checklist completa (ortografia, gênero, espaçamentos, nº de páginas, bibliografia não
cortada, datas, IMC, formatação da conclusão e dos quesitos). Se o veredito for AJUSTAR,
aplique as correções apontadas e rode o revisor de novo, até o veredito PRONTO (no máximo
3 rodadas). Só então avise o Dr. que o laudo está pronto. Esta etapa é obrigatória e nunca
deve ser pulada.

### Passo 8.5 — Blindagem automática (Advogado do Diabo + Defensor do Laudo), quando o desfecho for negativo ou controverso

Se o desfecho da conclusão NEGAR o benefício (Modelos 3, 4 ou 5: sem sequela, sem redução da capacidade, ou restituição integral) OU for CONTROVERSO (Art. 86 grau leve sem enquadramento no Anexo III, concausa, ou enquadramento discutível no quadro 6), rode a blindagem ANTES de entregar. O Modelo já foi decidido no Passo 5, então a condição é direta. Nos laudos favoráveis ao autor (com incapacidade ou redução reconhecidas), NÃO rodar esta etapa.

1. **Advogado do Diabo:** rode o subagente `advogado-do-diabo` (ferramenta Task/Agent) sobre o ODT gerado e a pasta dos autos. Ele assume o papel do advogado do autor, ataca o laudo por todos os ângulos (método e exame, autos, literatura contrária real, jurídico-formal, coerência interna) e gera um dossiê de vulnerabilidades em ODT (uso interno, em /tmp). SÓ ataca e relata; não edita o laudo.

2. **Defensor do Laudo:** em seguida, rode o subagente `defensor-do-laudo` passando o dossiê, o laudo ODT e a pasta dos autos, com o caminho de SAÍDA igual ao do laudo final (o script `reforcar_laudo_odt.py` preserva a versão pré-blindagem em `.bak`). Ele blinda o laudo ponto a ponto SEM inventar e SEM inverter o desfecho: reforça o achado objetivo com o que já existe nos autos, acrescenta literatura real favorável em nota de rodapé, fecha a linguagem vaga, torna as respostas autossuficientes e diminui o peso de documento da parte por telemedicina. O laudo blindado passa a ser o laudo final; a versão anterior fica no `.bak`.

3. **Revisão final do blindado:** rode de novo o subagente `revisor-laudo` sobre o laudo já blindado (as notas de rodapé podem acrescentar página; o script recalcula as folhas). Corrija até o veredito PRONTO. Esta é a revisão que vale para a entrega, e substitui a do Passo 8.

No resumo ao Dr. (Passo 9), informe: o caminho do dossiê em /tmp, os pontos mais perigosos, o que o Defensor reforçou (com as referências reais usadas, com PMID), os ataques que ficaram SEM defesa (fraqueza real, não inventar) e as pendências que dependem do Dr. (medidas a refazer, fotos ou documentos a anexar). Se algum ponto for decisão redacional do Dr. (por exemplo, acrescentar a nota de equiparação a acidente de trabalho versus manter "acidente de trajeto"), aponte a decisão em vez de impô-la.

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
O rótulo "Resposta:" E o texto da resposta ficam **AMBOS em itálico** (tudo dentro
do span CONC_IT). Regra do Dr. de 08/07/2026: o rótulo "Resposta:" NÃO fica reto, fica
em itálico junto com a resposta. O script `gerar_conclusao_odt.py` já recompõe cada
parágrafo com "Resposta: " + resposta dentro do span CONC_IT. Em edição manual do XML,
mover "Resposta: " para DENTRO do span CONC_IT (nunca deixar o rótulo fora do span).
NÃO tratar rótulo "Resposta:" em itálico como erro na revisão (é o correto agora).

### Regra 13 — Data da página 1: verificar SEMPRE

A data da página 1 deve ser conferida e corrigida para a data atual em todo laudo
processado. O formato correto é: "Cidade, DD de Mês de AAAA", SEMPRE por extenso e com o MÊS EM
MAIÚSCULA (primeira letra), e NUNCA numérica (nem "06/08/2026" nem "06.08.2026").
O DIA vai SEMPRE com dois dígitos (zero à esquerda): "06" e não "6", ex.:
"Blumenau, 06 de Agosto de 2026". Regra do Dr. de 06.08.2026 (reverte a de 02/07/2026, que pedia minúscula).
O script corrige automaticamente (data_hoje_extenso já zero-preenche o dia) — se a data
não for encontrada, alertar o Dr. Lino.

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
3. Quanto à Consolidação (ABMLPM + "No caso em tela...")

Ordem completa dos 12 blocos do texto:
1. P1 (fato gerador)
2. P2 (tratamento + sequela)
3. P3 (repercussão laboral)
4. P4 (boilerplate)
5. P5 (Decreto 3048/99)
6. "Dados de interesse pericial:"  ← 2 blanks antes deste
7. Item 1 (DID)
8. Item 2 (incapacidade)
9. "3. Quanto à Consolidação:"
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

REFORÇO (Dr., 16/07/2026, laudo George): a padronização vale para TODA caixa de
marcação de resposta, não só as óbvias. O padrão único é: vazia = 3 espaços
`( <text:s text:c="2"/>)` (mesma largura do `( X )`); marcada = `( X )`. Varrer o
documento e uniformizar TODAS as vazias (aparecem com 1, 2, 3 ou 4 espaços,
principalmente em laudos vindos de conversão .doc→ODT, onde `marcar_caixas_reu`
não localiza a seção e não roda): normalizar `( <text:s/>)` e
`( <text:s text:c="3"/>)` para `( <text:s text:c="2"/>)`, sem tocar nas `( X )`.

### Regra 21b — Espaçamento vertical dos quesitos do réu com caixas (8, 10, 11)

Nos quesitos do réu com caixas de marcação (tipicamente 8, 10 e 11 do INSS):
- A pergunta fica COLADA às caixas, SEM parágrafo vazio entre a pergunta e os parênteses.
- UMA linha em branco separa as caixas (ou a linha "Justifique...", no 11) da "Resposta:".
- Espaço após a caixa antes do texto: "(   ) Sim. Indique...", nunca ")Sim".
O `gerar_conclusao_odt.py` faz isso automaticamente na função `normalizar_espacamento_caixas_reu`
(chamada após `marcar_caixas_reu`): remove o vazio entre pergunta e caixas, garante o vazio antes
da "Resposta:" e corrige ")Sim"/")Não". Confirmado pelo Dr. em 04.08.2026 (laudo Jean Carlo
Pessatti). Ver [[feedback-espacamento-caixas-reu]].

### Regra 22 — Remover OBSERVAÇÕES PARA O PERITO antes de contar as folhas

A seção final "OBSERVAÇÕES PARA O PERITO" (notas internas do pré-laudo: pendências,
divergências de RG/endereço, CAT a confirmar etc.) NÃO vai no documento juntado aos
autos. SEMPRE removê-la ao finalizar. A ORDEM importa: PRIMEIRO cortar do parágrafo do
título `OBSERVAÇÕES PARA O PERITO:` até `</office:text>` e re-zipar cru; SÓ ENTÃO
recontar as páginas e atualizar o número em "Considerações finais" (a remoção costuma
reduzir uma folha). Confirmado pelo Dr. em 29/06 e reforçado em 30/06/2026.

Desde 05.09.2026 o `gerar_conclusao_odt.py` faz a remoção sozinho no início de `gerar()`, antes de
contar as folhas (a linha "observações: seção removida" aparece no log). O passo manual acima
continua valendo para laudo editado FORA do gerador (ex.: remoção de seção pelo entregar-laudo-eproc).

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
  inserir manualmente no content.xml um parágrafo com "Resposta: Prejudicado." INTEIRO
  dentro do span CONC_IT (rótulo e texto ambos em itálico), após a 2ª opção e antes do 8.1.
- **Q8.1** (Sim/Não): NÃO marcar o "Sim". Deixar somente a resposta (ex.: "Não é caso
  para reabilitar; o autor mantém capacidade para a mesma atividade...").
- **Q10 e Q11** (cada um com caixas Não/Sim): puxar os parênteses das caixas para cima,
  COLADOS à pergunta (remover o parágrafo vazio entre a pergunta e as caixas).

Nesses casos, as ÚNICAS caixas marcadas do réu ficam **2.7** (acidente de trabalho) e
**4.1** (capacidade plena). Para "colar" as caixas à pergunta, remover no content.xml o
`<text:p .../>` vazio entre o parágrafo da pergunta e o parágrafo da primeira caixa.

### Regra 24 — Quesito 8 do réu (casos COM redução/auxílio-acidente): inserir Resposta padrão

Confirmado pelo Dr. em 02/07/2026 (laudo Gisele Farias e demais da pauta Brusque 01.07).
Nos laudos de auxílio-acidente COM redução da capacidade (art. 86 ou Anexo III), o quesito
8 do réu ("Caso exista incapacidade permanente para a atividade habitual...", com as duas
caixas "Não há potencial" / "Existe potencial") NÃO tem campo "Resposta:" próprio no
template. Inserir, logo após as duas caixas e antes do 8.1, um parágrafo de resposta
(rótulo "Resposta:" E texto ambos em itálico, tudo dentro do span CONC_IT) com o texto EXATO:

> "Não é caso para reabilitar, pode fazer a mesma atividade que desenvolvia na época do
> acidente, porém com maior dificuldade para algumas operações."

As duas caixas do Q8 ficam VAZIAS (não marcar). Esse texto é neutro de gênero (serve para
autor e autora).

**Q11 do réu** (necessidade de acompanhamento permanente de terceiros): a resposta é apenas
**"Prejudicado."** (curta, sem acrescentar "o autor/a autora é independente..."). O Q10
segue "Prejudicado. Não há incapacidade permanente para toda e qualquer atividade."

**ATUALIZAÇÃO 27.08.2026:** o `gerar_prelaudo.py` passou a separar os sub-quesitos 8.1 e
8.2 em quesitos próprios, cada um com o seu campo "Resposta:" (função
`dividir_subquesitos`). Nos pré-laudos gerados a partir dessa data o Q8 já nasce com os
três campos. Em laudo ANTIGO, o 8 continua carregando 8.1 e 8.2 no mesmo parágrafo — ver
a Regra 26.

### Regra 25 — Nexo com lesão ou doença PRÉ-EXISTENTE: exigir o documento do estado anterior

Sempre que o dano discutido incidir sobre órgão, segmento ou função que JÁ estava doente
ou lesado antes do fato (olho operado, joelho já meniscectomizado, coluna já degenerada,
ombro já tendinopático), a pergunta pericial não é "o trauma pode ter piorado?", e sim
"existe documento que demonstre a piora?".

**Método obrigatório, nesta ordem:**

1. Levantar nos autos TODO documento anterior ao fato que descreva a função do órgão
   (acuidade visual, arco de movimento, força, laudo de imagem, perícia administrativa,
   AIH, pedido de cirurgia). Ver o item 6 do Passo 3: esses documentos costumam estar
   nos anexos escaneados.
2. Levantar os documentos CONTEMPORÂNEOS ao fato (boletim de pronto-socorro, ficha do
   SAMU, exames de imagem do dia, primeira perícia do INSS depois do acidente).
   Conferir lateralidade, região atingida e o que o exame do dia registrou sobre o
   órgão em discussão. Silêncio nesses documentos é achado, e deve ser dito.
3. Comparar o estado ANTES com o estado DEPOIS. Sem uma medida anterior e outra
   posterior da mesma função, não há como aferir agravamento.

**Como concluir quando falta a documentação comparativa:** reconhecer a possibilidade
e negar a certeza, nesta ordem e sem rodeios: (i) a sequela existe e está caracterizada;
(ii) a doença ou lesão já estava documentada antes do fato, citando data e teor do
documento; (iii) é possível, em tese, que o trauma tenha agravado o quadro; (iv) não há
exame anterior comparável ao posterior, faltando documentação que permita afirmar o
agravamento com a devida certeza; (v) por isso NÃO se estabelece nexo, sequer concausal.

Redação validada (laudo Luiz Eduardo Lopes, 25.08.2026):
"Eventual agravamento pelo trauma de <data> é possível, porém não demonstrado, faltando
documentação que permita afirmá-lo com a devida certeza. Não se estabelece, por isso,
nexo, sequer concausal, entre o acidente e <o dano>."

**Cuidados que valem sempre:**
- Relatório da parte que atribui o dano ao acidente APOIADO NA NARRATIVA DO PERICIANDO
  não prova nexo. Quando o próprio documento disser "o paciente relata", citar essa
  expressão: ela mostra a origem da informação.
- Conferir a LATERALIDADE nos documentos do dia do fato. Trauma do lado oposto ao órgão
  doente derruba a tese de agravamento.
- Concausa (art. 21, I, da Lei 8.213/91) exige contribuição DEMONSTRADA, não meramente
  possível. Possibilidade teórica não é concausa.

---

### Regra 26 — Respostas do réu: conferir SEMPRE o alinhamento quesito x resposta

O `gerar_conclusao_odt.py` casa cada resposta ao NÚMERO do quesito (âncora). Até 27.08.2026
ele casava por POSIÇÃO, e bastava o documento ter um campo "Resposta:" a menos que o JSON
para todas as respostas seguintes escorregarem de quesito. Foi o que aconteceu no laudo do
Nilson de Souza (pauta Indaial 26.08): o Q8 trazia 8.1 e 8.2 embutidos no mesmo parágrafo,
com um único "Resposta:", e as respostas do 9 ao 19 do réu saíram deslocadas em duas casas.

O que fazer agora:

- **Ler o log do gerador.** Quando um quesito com resposta não encontra campo no documento,
  sai a linha `ATENÇÃO -> reu: sem campo 'Resposta:' no documento para o(s) quesito(s) ...`.
  Nunca ignorar: significa que aquelas respostas ficaram DE FORA e as demais podem ter
  escorregado. A linha `rótulos não casaram (N campos x M respostas) — preenchido por ORDEM,
  CONFERIR` é o mesmo alerta em grau máximo.
- **Conferir na revisão final** o Q8/8.1/8.2 e a sequência do 9 ao 19: cada resposta tem de
  responder à sua própria pergunta. Erro típico do deslocamento: uma pergunta de DATA
  respondida com texto de limitação funcional, ou um "Prejudicado." num quesito que pede
  descrição.
- **Quesito que se responde só pela caixa marcada** (4 e 5 do réu): escrever `"resposta": "-"`
  no JSON. O gerador REMOVE o campo "Resposta:" em vez de deixá-lo vazio. Regra do Dr. de
  27.08.2026 — ele apagava esses campos à mão.
- **Q2 do réu:** a resposta NÃO começa com "Marcada a alternativa 2.7."; vai direto ao
  conteúdo da justificativa (a caixa marcada já diz a alternativa). Idem no Q4, que sequer
  leva resposta.
- **Quesito que já veio RESPONDIDO no pré-laudo** (ex.: Q1 do autor com "Resposta: Sim."): o
  gerador só preenche campos vazios. Casando por número isso não desloca mais as demais, mas o
  log vai acusar "sem campo" para aquele número: conferir se a resposta pré-existente é a
  desejada e, se quiser trocá-la, editar o content.xml, não o JSON. (Caso Yris Olivo, 07.08.2026.)

### Regra 27 — Literatura em nota de rodapé: conferir na FONTE o segmento, a autoria e os achados contrários

Antes de gravar qualquer referência (Modelo 5, Modelo D, blindagem do defensor-do-laudo), três
checagens obrigatórias, feitas no registro do artigo e não de memória:

1. O estudo cobre o SEGMENTO ANATÔMICO e o tipo de lesão do caso? Conferir o CID ou a região que o
   estudo usou para selecionar a casuística, não só o título. No caso Jean Brauvers (27.08.2026) o
   registro sueco citado (Alfort 2023) levantou fraturas dos dedos 2 a 5 (S62.6) e o laudo tratava
   de polegar (S62.5): a referência principal não cobria o caso.
2. Autoria e ano batem com a fonte? Duas das três referências daquele laudo estavam com autores
   trocados.
3. O mesmo resumo traz achados DESFAVORÁVEIS? Se traz (no Ipsen 1987: intolerância ao frio em 36%,
   dormência em 36%, dor à palpação em 26%), citá-los e afastá-los pelo exame do caso, em vez de
   omitir: citação seletiva é mais frágil do que citação completa afastada.

Referência que não cobre o segmento é pior do que nenhuma: transforma um ponto forte do laudo em
vício de fundamentação e sustenta sozinha um pedido de nova perícia.

### Regra 28 — Toda edição estrutural exige recontar as folhas

Sempre que uma edição mudar o número de páginas (remover a seção de quesitos do réu, acrescentar
notas de rodapé, responder quesitos supervenientes), recontar o page_count do PDF e atualizar
"constituído de N (por extenso) folhas" nas Considerações finais. O texto costuma estar
fragmentado num `<text:span>`; substituir com o span. O revisor-laudo cruza o número declarado com
o real. Caso Manoel, Pomerode, 10.08.2026 (18 para 14 folhas).

### Regra 29 — Localizar o laudo a editar por chave ÚNICA, nunca pelo primeiro nome

Os arquivos se chamam "LAUDO MÉDICO <primeiro nome>.odt" em todas as pautas, e a pasta da pauta é
renomeada depois da perícia (cai o horário e entra o sufixo " ok"). Buscar por substring do primeiro
nome pegou o periciando errado em 05.08.2026 (dois "Marcio", Indaial e Rio do Sul; o já entregue
foi alterado e teve de ser revertido). Regra: casar pelo nome COMPLETO mais a pauta (comarca e
data); havendo mais de um candidato, listar todos e confirmar antes de escrever; antes de gravar,
conferir no conteúdo um dado-âncora do caso (nº dos autos); editar sobre cópia em /tmp e só então
copiar para a pasta. Pautas concluídas saem do LINO (arquivadas): edição retroativa pode não ser
possível localmente.

### Regra 30 — Cabeçalho: o que sobrevive ao editor do Dr., e o que não sobrevive

Consolidado dos casos Mirela, Juliana, Dilmar, Leonardo e Viviane (31.07 a 24.08.2026):

- SOBREVIVE ao open/save do Apache OpenOffice: frame `as-char` dentro de `text:p` Standard, com
  `xlink:href` completo, PNG presente no zip e entrada no manifest, e o estilo gráfico do frame
  definido por inteiro (é o que o gerador escreve e o que `normalizar_peca_lino.py` reconstrói).
- NÃO sobrevive: frame com href já vazio ou quebrado (o render tolerante do LibreOffice esconde o
  defeito, mas o save do OpenOffice esvazia o `draw:image` e descarta a pasta Pictures); e a
  imagem de FUNDO do parágrafo (HdrLogoBg) não renderiza no OpenOffice do Dr.
- "logo: header sem frame de logo" no log do gerador NÃO é alarme quando o timbre é
  `<style:background-image>` dentro do estilo de parágrafo do header (templates com MP1 e altura
  de linha de 2,701 cm, como a pauta Blumenau 18.08): o logo renderiza em todas as páginas. O
  `restaurar_logo.py` reconhece essa variante desde 05.09.2026.
- Header TOTALMENTE zerado (`<style:header><text:p/></style:header>`, sem frame e sem PNG): o
  `restaurar_logo.py` reconstrói o frame canônico do zero (05.09.2026); antes disso a
  reconstrução era manual (caso Leonardo, 05.08.2026).
- "Resolvido" só vale no ambiente em que o Dr. edita: validar por round-trip real no OpenOffice
  dele, não pelo render do LibreOffice. Antes de declarar uma pauta "cabeçalho ok", conferir por
  arquivo href válido e PNG no pacote.

### Regra 31 — Auxílio-acidente: o retorno ao trabalho habitual NÃO é argumento contra a redução

Correção do Dr. em 17.09.2026, depois de várias respostas a quesitos e manifestações que usavam
esse argumento.

O auxílio-acidente indeniza justamente quem SEGUE trabalhando, porém com maior dificuldade para o
trabalho que habitualmente exercia. Voltar ao trabalho habitual, permanecer na mesma função ou no
mesmo empregador, não ter novo afastamento ou não ter sido readaptado NÃO demonstra que inexiste a
maior dificuldade. Demonstra apenas que a pessoa segue trabalhando, que é exatamente a situação que
o benefício pressupõe.

Vale para QUALQUER peça de auxílio-acidente: Discussão/Conclusão, quesitos do Juízo, do autor e do
réu, quesitos complementares, manifestação à impugnação e blindagem (Advogado do Diabo e Defensor
do Laudo).

- NUNCA usar o retorno ao trabalho, a permanência na mesma função ou empregador, a ausência de novo
  afastamento ou de readaptação como fundamento, reforço ou "munição" para negar ou minimizar a
  redução da capacidade, nem sob o rótulo de "capacidade específica".
- A ausência de redução (Modelos 3, 4 e 5) se sustenta SÓ no que mede a sequela: exame pericial
  (goniometria, força, manobras), exames de imagem, documentos médicos contemporâneos e literatura
  do segmento.
- O retorno pode constar como FATO (anamnese, histórico ocupacional, tabela 5.1) e na resposta ao
  quesito que pergunta diretamente se a pessoa voltou a trabalhar ("Sim, retornou à mesma função
  em DD.MM.AAAA."), sem tirar dele conclusão sobre a capacidade.
- Quesito que usa o retorno como premissa ("se voltou à mesma função, não há redução?"): responder
  que o retorno ao trabalho, por si só, não afasta a redução da capacidade, e que a conclusão se
  funda no exame pericial.
- Nas conclusões COM redução (Modelos 1 e 2), segue valendo o reverso validado no caso Rosângela
  Schmitt (09.09.2026): o retorno ao trabalho não afasta a redução; a permanência no emprego prova
  aptidão global, não integridade do segmento.

**Conferência antes de entregar:** buscar no texto novo "retorn", "voltou", "mesma função",
"mesma atividade", "mesmo empregador", "novo afastamento", "segue trabalhando", "continua
trabalhando" e "readapt". Cada ocorrência tem de ser só fato; nenhuma pode sustentar a ausência
ou a pequena monta da redução.

### Respostas padrão adicionais confirmadas (laudo Nelson Heinert — junho/2026):

| Quesito | Resposta exata validada |
|---|---|
| Q6 Juízo (natureza da incapacidade) | "É Parcial e Permanente." |
| Q16 autor (PCD reconhecido pelo empregador) | "Sim." |

---

## AUXÍLIO-ACIDENTE — OS 4 TIPOS OBRIGATÓRIOS DE CONCLUSÃO

Quando o pedido for AUXÍLIO-ACIDENTE, a Discussão/Conclusão deve obrigatoriamente seguir UM destes 4 modelos. Em todos eles, o retorno ao trabalho habitual NÃO é argumento contra a redução da capacidade (Regra 31). A diferença entre os modelos 1 e 2 é exclusivamente o enquadramento ou não no Anexo III do Decreto 3048/99.

### MODELO 1 — Redução de capacidade COM enquadramento no Anexo III (exemplo: LAUDO IZAIAS)
Após a frase de impacto e o parágrafo-ponte ("Com base nas informações obtidas na anamnese durante a expertise médico pericial, tomando-se por base a minudente análise retrospectiva documental e notadamente pelo exame físico geral e segmentar descrito no corpo do laudo técnico, como prerrogativa do Perito deste Juízo, este avaliador técnico de confiança do Magistrado conclui que:"):

> "O autor possui sequela que se enquadra tecnicamente no quadro [N] do Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

OBRIGATÓRIO: citar o número do quadro correto E transcrever a alínea exata logo abaixo. Exemplo (perda do polegar — quadro 5):
> "b) perda de segmento do primeiro quirodáctilo, desde que atingida a falange proximal; (Redação dada pelo Decreto nº 4.032, de 2001)"

**Demonstração aritmética do grau (quadro 6, regra de 21.08.2026, laudo Ivanor Seidler):** o enquadramento é uma razão entre arcos medidos, não impressão clínica. Escrever na conclusão o cálculo comparativo lado a lado (arco do lado acidentado x arco do lado íntegro), a perda em percentual e a classificação (mínimo até 1/3; médio acima de 1/3 até 2/3; máximo acima de 2/3), no formato espaçado das regras de redação, com o resultado em negrito. Enquadrar SÓ as articulações cujo grau atinge médio ou máximo e citar as demais como redução que não alcança o corte (no Ivanor: prono-supinação 100 contra 180 graus = perda de 44%, grau médio, enquadra na alínea e; tibiotársica 35 contra 40 graus = 12%, mínimo, não enquadra). A NOTA 2 do quadro 6 (fratura de osso longo consolidada) é fundamento adicional quando a articulação é punho, prono-supinação, cotovelo, joelho ou tibiotársica com fratura próxima.

Seguir com "Dados de interesse pericial:" — 1. DID estimada na data do acidente; 2. incapacidade total e temporária do acidente até a DCB; após a DCB, parcial e permanente que não impede o trabalho habitual, porém com maior dificuldade para algumas operações; 3. Consolidação: citar o conceito da ABMLPM ("Consolidação médico-legal da lesão, é quando, finalizados os tratamentos, esgotando-se as medidas terapêuticas atuais e disponíveis, não se vislumbrando evolução para melhora da lesão, configurando-se a sequela, um dano permanente.") e estimar a consolidação na DCB pelo critério da compatibilidade anatomoclínica.

### MODELO 2 — Redução de capacidade SEM enquadramento no Anexo III, COM Art. 86 (exemplo VALIDADO: LAUDO CLEITON GRAF, pauta Brusque 01.07.2026)

Usar quando HÁ redução real da capacidade para o trabalho habitual decorrente de acidente, mas a sequela NÃO se enquadra em nenhum quadro do Anexo III. Casos típicos: anquilose ou amputação isolada do 3º, 4º ou 5º quirodáctilo (o quadro 5 exige dois quirodáctilos, ou o 1º/2º isoladamente); limitação articular em grau apenas leve; sequela do dedo mínimo com força de preensão preservada (afasta o quadro 8).

**ATENÇÃO (correção do Dr., laudo Cleiton Graf, 15.07.2026):** o texto antigo deste modelo estava ERRADO. Este modelo USA o parágrafo-ponte boilerplate (NÃO vai "direto após a frase de impacto"), NÃO usa "mínima redução" SOZINHA sem o Art. 86 (com o Art. 86 presente logo abaixo, pode e deve citar o grau leve/mínima, ver regra de 05.08.2026 abaixo) e SEMPRE cita o Art. 86 da Lei 8213/91. O art. 86 é MAIS AMPLO que a lista do Anexo III: qualquer redução da capacidade para o trabalho habitual decorrente de acidente de qualquer natureza dá direito ao auxílio-acidente pelo art. 86, mesmo sem enquadramento no Anexo III. Concluir "não possui enquadramento no Anexo III" SEM o art. 86 soa como negativa indevida do benefício.

Estrutura: P1 a P3 iguais ao Modelo A (fato gerador/CID; tratamento e sequela com "Embora tenha realizado..."; repercussão no trabalho habitual com "Tal sequela gera..."), seguidos do parágrafo-ponte boilerplate ("Com base nas informações obtidas na anamnese durante a expertise médico pericial, ... este avaliador técnico de confiança do Magistrado conclui que:") e, então, destes três blocos, nesta ordem:

> "Embora exista sequela que gera **leve** redução da capacidade laborativa da parte autora, esta não possui enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)." (Usar **leve** ou **mínima** conforme o caso.)

**REGRA DO DR. (05.08.2026, laudo Damião Galdino):** nos casos de MÍNIMA redução da capacidade (perda de mobilidade de dedo, perda de parte de falange e similares), SEMPRE citar o grau da redução da capacidade laborativa, "leve" ou "mínima", neste bloco do Art. 86. Isto NÃO contradiz a correção de 15.07 (parágrafo ATENÇÃO acima): o que se proibiu foi "mínima redução... não possui enquadramento" SOZINHA, sem o Art. 86 (soava como negativa do benefício); aqui o Art. 86 vem logo abaixo e concede o benefício, então o grau apenas QUALIFICA a redução. Ver [[feedback-incapacidade-parcial-permanente-resposta]].

> "Tal situação, no entanto, se enquadra no Art. 86 da Lei 8213/1991."

> "Art. 86. O auxílio-acidente será concedido, como indenização, ao segurado quando, após consolidação das lesões decorrentes de acidente de qualquer natureza, resultarem seqüelas que impliquem redução da capacidade para o trabalho que habitualmente exercia."

"Dados de interesse pericial:" com os mesmos 3 itens do Modelo A: 1. DID na data do acidente (com "no dia"); 2. incapacidade total e temporária do acidente até a DCB, depois parcial e permanente que não impede o trabalho habitual, porém com maior dificuldade para algumas operações (com "no dia"); 3. consolidação: conceito da ABMLPM + "Estima-se a consolidação do quadro na DCB, em DD.MM.AAAA." (a data da consolidação vai SEM "dia" antes). Quesito sobre natureza da incapacidade: "É parcial e permanente." (acrescentar "grau mínimo" quando a redução for realmente mínima).

**Variante do Modelo 2: sequela anatômica permanente com exame funcional NORMAL** (meniscectomia parcial, reconstrução ligamentar, ressecção óssea, com ADM completa, força 5/5 e manobras negativas). Redação validada no caso Leomar Alves Batista (29.07.2026): a redução é MÍNIMA e se funda na perda anatômica (reserva funcional para esforços intensos), sem afirmar limitação de amplitude ou instabilidade que o exame não mostrou, reconhecendo o bom resultado funcional para não contradizer o exame. ATENÇÃO: há precedente do Dr. em sentido oposto (caso Johann, menisco operado sem sequela = Modelo 5). Em exame normal com benefício contestado, a direção (Modelo 2 com redução mínima x Modelo 3/5 sem redução) é decisão do Dr.: entregar a versão mais defensável pelos achados e DESTACAR a alternativa no resumo, nunca escolher em silêncio. Quando a declaração do assistente da parte divergir do exame do perito, gradar pela clínica própria.

**Sub-tipo: REVISÃO DO DIP de auxílio-acidente já concedido.** O autor já recebe o benefício e pede a retroação do termo inicial. O papel do perito é DATAR a consolidação na DCB do auxílio-doença anterior (ex.: B91 cessado em 31.10.2016) e explicitar que, pelo art. 86, parágrafo 2º, o auxílio-acidente é devido a partir do dia seguinte à cessação do auxílio-doença. O restante da conclusão segue o Modelo 2 ou o Modelo 1 conforme o enquadramento.

### MODELO 3 — SEM perda de funcionalidade e SEM redução de capacidade (exemplo: LAUDO ELISA)
Antes da frase-ponte: "Foi realizado o devido tratamento e não restaram limitações funcionais." Frase-núcleo:

> "A autora não possui lesão ou sequela que possa ser classificada como incapacitante ou que reduza sua capacidade para o trabalho habitual, não havendo, assim, enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

Sem "Dados de interesse pericial". Quesitos sobre incapacidade: "Prejudicado".

**Variação: houve incapacidade temporária COM benefício e consolidou sem sequela** (caso Denis Kertzendorff, queimaduras por arco elétrico, 31.07.2026). Omitir os "Dados de interesse pericial" apagaria da conclusão a DID e o afastamento que constam dos autos. INCLUIR um bloco curto, no formato do Modelo 5: 1. DID na data do acidente; 2. incapacidade total e temporária do acidente até a DCB, com consolidação e restituição integral na DCB. SEM o boilerplate ABMLPM de "sequela, um dano permanente", que afirmaria sequela inexistente.

**Sequela apenas ESTÉTICA (cicatriz de queimadura, corte, enxerto em membro):** acrescentar um parágrafo afastando expressamente o quadro 4 do Anexo III, que só enquadra prejuízo estético de grau médio ou máximo em crânio, face ou pescoço; cicatriz leve em segmento de membro não enquadra. Casos de queimadura que curam com cicatriz são arquétipo recorrente.

### MODELO 4 — Perda de funcionalidade que NÃO gera redução de capacidade laborativa
Descrever a perda funcional objetivada ao exame (ex.: discreta limitação de amplitude, cicatriz, hipotrofia) e registrar que não interfere nas operações da atividade habitual. Frase-núcleo:

> "O autor possui perda de funcionalidade decorrente da lesão, porém tal perda não gera redução de sua capacidade para o trabalho habitual, não havendo, assim, enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."

### MODELO 5 — Consolidação com restituição integral (restitutio ad integrum) + fundamentação científica OBRIGATÓRIA (exemplo: LAUDO TAÍSE, laceração hepática)

Aplica-se sempre que a lesão do acidente CONSOLIDOU-SE com restituição integral, ou seja, o tratamento foi realizado e NÃO restou qualquer limitação funcional ao exame pericial (fratura consolidada sem sequela, luxação reduzida sem sequela, laceração de víscera cicatrizada, TCE leve sem sequela, lesão meniscal ou ligamentar operada com exame atual normal, etc.). É um caso "sem redução da capacidade" (como o Modelo 3), porém com acréscimos obrigatórios definidos pelo Dr. Lino em 01/07/2026:

**Segundo exemplo validado (laudo Johann Buetes Arndt, 29/07/2026):** rotura em alça de balde do menisco lateral do joelho direito (CID S83.2) em atleta profissional de futebol, operada e consolidada sem sequela (exame do joelho inteiramente normal: McMurray, gaveta e Lachman negativos, movimentos completos, força 5/5). Fundamentação com 3 revisões sistemáticas reais do PubMed sobre retorno ao esporte após cirurgia meniscal em atletas de elite (menisco lateral, alto potencial de cicatrização; retorno de 86 a 89% ao nível prévio). Confirma que o Modelo 5 é indexado pelo DESFECHO (consolidação com restituição integral), não pela profissão.

REGRA ABSOLUTA (vale para TODO caso de restitutio ad integrum): antes de redigir, BUSCAR na literatura, usando as ferramentas/APIs do PubMed (mcp__claude_ai_PubMed__*) ou do Consensus (mcp__claude_ai_Consensus__search), evidência científica de que AQUELE TIPO de lesão tem altíssima probabilidade de consolidar SEM limitação funcional. Trazer esses dados como parágrafo técnico na Discussão/Conclusão, fundamentando a ausência de sequela. Nunca inventar referência: usar somente artigos reais retornados pelas ferramentas, com autores, ano e periódico corretos.

1. FUNDAMENTAÇÃO CIENTÍFICA no corpo da conclusão, com CITAÇÃO NUMÉRICA [1], [2], [3] logo após as afirmações.
2. As REFERÊNCIAS correspondentes vão em NOTA DE RODAPÉ (ao pé da página onde são citadas), NÃO na seção Bibliografia.

Estrutura da Discussão/Conclusão (ver exemplo Taíse):
- Parágrafo 1: o fato (acidente, lesão, tratamento realizado).
- Parágrafo 2: evolução com consolidação; exame pericial atual SEM limitações funcionais objetivadas. O retorno à atividade pode ser citado como fato, nunca como o que prova a ausência de sequela (Regra 31).
- Parágrafo 3 (científico): afirmação técnica sobre a estrutura lesada [1]; "A literatura médica demonstra que [tipo de lesão] evolui com cicatrização/consolidação ... [2], com retorno pleno às atividades habituais ... [3]. Trata-se, portanto, de lesão com altíssima probabilidade de consolidação sem sequela funcional, o que se confirma no presente caso."
- Parágrafo 4 (núcleo, igual ao Modelo 3): "... não possui lesão ou sequela que possa ser classificada como incapacitante ou que reduza sua capacidade para o trabalho habitual, não havendo, assim, enquadramento técnico no Anexo III do Decreto 3048/99 (Relação de situações que dão direito ao Auxílio-acidente)."
- "Dados de interesse pericial:" 1. DID na data do acidente; 2. consolidação estimada na DCB, compatível com o tempo de cicatrização descrito na literatura.

Quesitos: mesmo padrão dos Modelos 3/4 (Regra 23), só 2.7 e 4.1 marcadas; quesitos de incapacidade "Prejudicado"; Q8 com as duas opções coladas à pergunta e "Resposta: Prejudicado."; Q10/Q11 caixas coladas.

COMO GERAR AS NOTAS DE RODAPÉ (o gerar_conclusao_odt.py não faz nota de rodapé nativamente):
- No texto da conclusão, deixar os marcadores [1], [2], [3] inline.
- Após rodar o gerar_conclusao_odt.py, pós-processar o content.xml do ODT (o documento já traz text:notes-configuration com text:footnotes-position="page"). Substituir cada marcador " [n]" por:
  <text:note text:id="ftnN" text:note-class="footnote"><text:note-citation>N</text:note-citation><text:note-body><text:p text:style-name="Nota_Rodape">REFERÊNCIA</text:p></text:note-body></text:note>
  definindo o estilo Nota_Rodape (Arial 10pt, justificado) em office:automatic-styles. Re-zipar cru (mimetype primeiro).
- Recontar as folhas (as notas podem acrescentar uma página) e atualizar "N (por extenso) folhas" nas Considerações finais.


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
2. O LAUDO VALDIR contém erro ("se enquadra no quadro 6") — amputação ou anquilose isolada do 5º quirodáctilo NÃO se enquadra no Anexo III. Nesses casos de redução SEM Anexo III, o exemplo VALIDADO é o LAUDO CLEITON GRAF (Modelo 2 COM Art. 86 da Lei 8213/91). O antigo LAUDO ADEMAR não citava o art. 86 e não deve mais ser usado como referência do Modelo 2 (atualizado em 15.07.2026).

### CONVENÇÃO DE COMANDO
Dr. Lino pode indicar o modelo diretamente no comando (ex.: "conclusao1 modelo 2") — usar o modelo indicado sem questionar. No modelo 1, mesmo com modelo indicado, identificar e citar SEMPRE o quadro e a alínea corretos do Anexo III conforme a lesão. Se o modelo não for indicado, classificar pelo exame físico/autos e informar qual modelo foi aplicado; em dúvida entre dois modelos, perguntar antes.


## Estilo de redação (regra transversal do Dr. Lino)

Vale para TODO texto que esta skill produz (laudo, parecer, conclusão, quesitos, manifestação):

- Escrever POUCO por parágrafo e dar um leve espaçamento entre eles. Texto longo e corrido não é lido. Um raciocínio por parágrafo, parágrafos curtos, com linha em branco entre os blocos.
- CÁLCULOS sempre espaçados, passo a passo (cada etapa em sua linha), e com o RESULTADO em NEGRITO ao final.
- FECHAR cada item/argumento com uma frase conclusiva, curta e em NEGRITO, que crava o ponto: "Portanto, fica bem claro que a valoração correta é de XXXX." / "Como pode ser visto, o Expert errou nesse ponto." O leitor tem de sair de cada item sabendo exatamente a conclusão.


## Regras de redação padronizadas (Dr. Lino — 16.07.2026)

Valem para todo texto produzido por este skill (laudos, pré-laudos, pareceres, conclusões e quesitos):

- **Datas com ponto:** escrever sempre no formato 16.05.2019, nunca 16/05/2019. É a preferência do Dr. (ele usa o ponto, não a barra).
- **Moto, não motocicleta:** usar o termo "moto" (mais coloquial); nunca "motocicleta".
- **Ordem cronológica crescente nas tabelas (pré-laudos):** as tabelas de exames, de documentos/atestados, de benefícios e de vínculos empregatícios (CNIS) saem sempre do mais antigo (no topo) para o mais recente (no fim). Os geradores de pré-laudo já ordenam e convertem as datas para o ponto automaticamente; ao montar o JSON, informar os itens já em ordem crescente.
