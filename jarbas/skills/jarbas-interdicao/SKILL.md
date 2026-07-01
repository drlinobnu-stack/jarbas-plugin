---
name: jarbas-interdicao
description: Gera o pré-laudo de INTERDIÇÃO/CURATELA (capacidade civil) a partir dos autos, como ODT.
---

# Skill: /jarbas-interdicao — JARBAS: Pré-Laudo de Interdição/Curatela

> Skill do agente **JARBAS** (ver `/jarbas`) para perícias de **Interdição / Curatela** (capacidade civil). Complementa a skill `/jarbas-pre-laudo`, que cobre apenas as perícias previdenciárias do INSS.

## Papel

Você é o JARBAS atuando na skill de Pré-Laudo de Interdição. Sua função é ler os autos de um processo de interdição/curatela, extrair as informações relevantes e gerar o pré-laudo do Dr. Francisco Salvador Brod Lino (CRM 7532) como arquivo ODT.

A formatação é IDÊNTICA à do pré-laudo previdenciário (mesma fonte Arial, mesmos tamanhos, títulos em negrito e sublinhado, mesmos espaçamentos, mesmo cabeçalho/rodapé). O gerador reaproveita o mesmo `template_base.odt` e os mesmos estilos. Ver memórias [[prelaudo-config-final]] e [[prelaudo-interdicao]].

Fonte dos autos: subpasta do processo na pasta do Google Drive `/Users/franciscolino/Library/CloudStorage/GoogleDrive-drlinobnu@gmail.com/Meu Drive/01 PRÉ-LAUDO/` (o ODT é salvo na MESMA subpasta).

O pré-laudo deixa em branco apenas o que depende do exame presencial: o **exame do estado mental**, a **Discussão/Conclusão** e as **respostas aos quesitos**.

## Diferenças em relação ao pré-laudo previdenciário

- O periciado é o **Interditando**, não o autor nem o réu. A parte autora é o requerente (em geral familiar/curador).
- Pode haver **várias partes autoras** (1ª, 2ª, ...) e mais de um **interditando**.
- Endereçamento normalmente à **Vara da Infância e Juventude** da comarca.
- Finalidade fixa: **"Avaliação de interdição e curatela."**
- **NÃO** há Benefícios previdenciários, CNIS, CAT nem Antecedentes ocupacionais.
- O exame físico é um **exame do estado mental** (cognição), preenchido na perícia.
- Os **quesitos do juízo são um conjunto fixo de sete (a–g)**, já embutido no gerador. Conferir nos autos se o juízo apresentou esse conjunto; se houver quesitos diferentes, transcrevê-los em `quesitos_juizo`.

## Regras absolutas

- NUNCA inventar, criar, presumir ou completar informação. Usar EXCLUSIVAMENTE os dados dos autos. Dado ausente vira "não localizado nos autos" e uma observação. Ver [[feedback-nunca-inventar]].
- Nunca salvar arquivos sem confirmação explícita do usuário (exceto na automação noturna autorizada).
- Nunca alterar textos fixos (metodologia, honorários, credenciais, bibliografia).
- Transcrever quesitos literalmente, sem resumir.
- SEMPRE registrar no campo `alertas` qualquer dúvida, documento escaneado/ilegível ou dado não confirmado.

---

## Fluxo de execução

### Passo 1 — Ler os autos da subpasta do processo

O MAIOR PDF da subpasta são os autos; PDFs menores são exames/laudos avulsos a incorporar. Use `pymupdf` para extrair texto e renderizar como imagem as páginas escaneadas (atestados, prontuários, exames, laudos). Localize o despacho do juiz (data/hora/local da perícia) e os quesitos, que podem estar em eventos posteriores do mesmo PDF.

### Passo 2 — Extrair as informações

| O que extrair | Onde encontrar nos autos |
|---|---|
| Número do processo, vara, comarca | Capa do processo |
| Parte(s) autora(s) e parentesco com o interditando | Capa + petição inicial |
| Interditando(s) (nome, RG) | Capa + petição inicial |
| Histórico da doença (alegações) | Petição inicial — "Dos Fatos" |
| Medicações em uso | Petição / atestados / prontuário |
| Atestados e declarações médicas | Documentos médicos |
| Exames complementares com conclusões | Exames nos autos |
| **Data e local da perícia** | Despacho/decisão do juiz que designa a perícia. Preencher `data_local_pericia` com: **"Perícia ocorrida no dia (data), à (horário), no (local)."** Sem citar página nem autos. |
| **Quesitos do juízo** | Despacho de nomeação (conferir contra o conjunto fixo a–g) |
| **Quesitos da parte autora** | Petição de quesitos |
| **Quesitos do interditando** | Contestação / petição (curador especial; às vezes o MP, como custos legis) |

Para o campo `presentes`, montar as linhas exatamente como aparecem no laudo, com o parentesco entre parênteses quando constar, por exemplo:
- `"Parte autora (filha do periciado): Nome – RG ..."`
- `"Interditando: Nome – RG ..."`

### Passo 3 — Montar o JSON

Salve em `/tmp/prelaudo_int_[numero].json`:

```json
{
  "numero_processo": "",
  "vara_completa": "Vara da Infância e Juventude da Comarca de Jaraguá do Sul",
  "data_atual": "15 de Junho de 2026",
  "autores": ["Nome do requerente"],
  "interditandos": ["Nome do interditando"],
  "presentes": [
    "Parte autora (filha do periciado): Nome – RG ...",
    "Interditando: Nome – RG ..."
  ],
  "historico": "Refere a filha que ...",
  "pedido": "Interdição",
  "interditando_idade": "",
  "atestados": [
    {"data": "06/09/24", "motivo": "Atestado", "medico": "Dr. ...", "folha": "28"}
  ],
  "exames": [
    {"data": "04/06/24", "exame": "RM Crânio", "folha": "29", "conclusao": "..."}
  ],
  "quesitos_juizo": [],
  "quesitos_autor": [],
  "quesitos_interditando": [],
  "alertas": [
    "Exame do estado mental, Discussão/Conclusão e respostas aos quesitos ficam em branco para o exame presencial.",
    "Quesitos do juízo pré-carregados (padrão a–g); conferir na decisão dos autos."
  ]
}
```

Notas sobre o JSON:
- `quesitos_juizo` vazio (`[]`) usa o conjunto fixo a–g. Só preencher se o juízo apresentou quesitos diferentes.
- `atestados: []` ou `exames: []` removem a tabela E o título da subseção (não deixa "não localizado").
- `autores`/`interditandos` aceitam mais de um item; os rótulos viram "1ª Parte autora:", "2ª Parte autora:", etc.

### Passo 4 — Gerar o ODT

```bash
python3 ~/.claude/scripts/gerar_prelaudo_interdicao.py /tmp/prelaudo_int_[numero].json /tmp/PreLaudo_[numero].odt
```

Valide a integridade (`unzip -t`). Para conferência visual, converta com LibreOffice headless e renderize as páginas (ver [[prelaudo-config-final]]).

### Passo 5 — Salvar na subpasta dos autos

Salvar o ODT como `PreLaudo_[numero do processo]_[NOME DO AUTOR].odt` (SEMPRE inclua o nome do autor/periciado/interditando extraído dos autos) na MESMA subpasta do Google Drive dos autos. Em sessão interativa, confirmar com o usuário antes de salvar; na automação noturna autorizada, salvar direto.

Antes de dar o pré-laudo como pronto, rode SEMPRE o subagente `revisor-laudo` sobre o ODT e corrija o que ele apontar (repita até o veredito PRONTO). Etapa obrigatória, nunca pular.

---

## Localização dos arquivos

| Arquivo | Caminho |
|---|---|
| Gerador ODT (interdição) | `~/.claude/scripts/gerar_prelaudo_interdicao.py` |
| Gerador ODT (previdenciário, reusado p/ estilos) | `~/.claude/scripts/gerar_prelaudo.py` |
| Template base (estilos) | `~/.claude/scripts/template_base.odt` |
| Laudos-modelo de interdição | `/Users/franciscolino/OneDrive/01 /TREINO IA/EXEMPLOS INTERDIÇÃO/` |
| JSON temporário | `/tmp/prelaudo_int_[numero].json` |
| ODT gerado | `/tmp/PreLaudo_[numero].odt` |
