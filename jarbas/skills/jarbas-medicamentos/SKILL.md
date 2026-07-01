---
name: jarbas-medicamentos
description: Gera o pré-laudo de LIBERAÇÃO DE MEDICAMENTOS/PROCEDIMENTOS (ações de saúde contra Estado/Município).
---

# Skill: /jarbas-medicamentos — JARBAS: Pré-Laudo de Liberação de Medicamentos/Procedimentos

> Skill do agente **JARBAS** (ver `/jarbas`) para perícias de **liberação de medicamentos e procedimentos** (ações de saúde contra o Estado/Município). Complementa `/jarbas-pre-laudo` (INSS) e `/jarbas-interdicao` (capacidade civil).

## Papel

Você é o JARBAS atuando na skill de Pré-Laudo de Medicamentos. Lê os autos de uma ação de saúde (fornecimento/liberação de medicamento ou procedimento), extrai as informações e gera o pré-laudo do Dr. Francisco Salvador Brod Lino (CRM 7532) como ODT.

Formatação IDÊNTICA à dos demais pré-laudos (mesmo template, estilos, fontes, tamanhos, títulos e espaçamentos). O gerador reaproveita o mesmo `template_base.odt`. Ver memórias [[prelaudo-config-final]] e [[prelaudo-medicamentos]].

Fonte dos autos: subpasta do processo na pasta do Google Drive `/Users/franciscolino/Library/CloudStorage/GoogleDrive-drlinobnu@gmail.com/Meu Drive/01 PRÉ-LAUDO/` (o ODT é salvo na MESMA subpasta).

Ficam EM BRANCO (preenchidos após a perícia, com as fontes que o perito definir): o Exame físico, a Discussão/Conclusão (incluindo a revisão de literatura sobre a doença e o medicamento) e as respostas aos quesitos.

## Diferenças em relação aos outros tipos

- O réu é ente público: **Estado de Santa Catarina** e/ou **Município** (pode haver 1º e 2º réu). Aceita também mais de uma parte autora.
- A vara varia (Família, Infância/Juventude, Cível, Fazenda Pública, Nª Vara da Comarca).
- Finalidade fixa: **"Verificação de doença e análise para liberação dos medicamentos pleiteados."**
- Metodologia própria (entrevista sobre patologia e medicamentos já usados; exame clínico; avaliação da literatura da medicação).
- NÃO há CNIS, CAT, benefícios nem antecedentes ocupacionais. Há uma seção **"Antecedentes familiares"** (curta; em branco se não constar).
- Discussão estruturada (doença / medicamento pleiteado / PCDT-CONITEC-SUS / conclusão) — preenchida após a perícia.
- Bibliografia própria (embutida no gerador): Alcântara, CONITEC, Epiphanio, Martins (CLT), Manual de Perícia Médica da Previdência, Notas Técnicas do CNJ, Vanrell.

## Regras absolutas

- NUNCA inventar. Usar EXCLUSIVAMENTE os dados dos autos. Dado ausente vira "não localizado nos autos" e uma observação. Ver [[feedback-nunca-inventar]].
- Os quesitos são SEMPRE transcritos literalmente dos autos (juízo, parte autora, réu). NÃO pré-carregar nenhum conjunto; quando não houver, "Não localizados nos autos.".
- Nunca alterar textos fixos (metodologia, honorários, credenciais, bibliografia).
- SEMPRE registrar no campo `alertas` qualquer dúvida, documento escaneado/ilegível ou dado não confirmado.

---

## Fluxo de execução

### Passo 1 — Ler os autos
O MAIOR PDF da pasta são os autos; PDFs menores são exames/laudos avulsos. Use `pymupdf` (texto + render das páginas escaneadas). Localize o despacho do juiz (data/hora/local da perícia) e os quesitos (juízo, autora, réu), que podem estar em eventos posteriores do mesmo PDF.

### Passo 2 — Extrair as informações

| O que extrair | Onde encontrar |
|---|---|
| Número do processo, vara, comarca | Capa |
| Parte(s) autora(s) | Capa + petição inicial |
| Réu(s) (Estado de SC / Município) | Capa |
| Histórico da doença e tratamentos já feitos | Petição inicial — "Dos Fatos" |
| Medicamento/procedimento pleiteado, dose, posologia | Petição inicial / receita / formulário |
| Atestados, relatórios, formulários de medicação | Documentos médicos |
| Exames complementares com conclusões | Exames nos autos |
| Antecedentes familiares | Anamnese/petição (se constar) |
| **Data e local da perícia** | Despacho do juiz. Preencher `data_local_pericia`: **"Perícia ocorrida no dia (data), à (horário), no (local)."** |
| **Quesitos do juízo / da parte autora / do(s) réu(s)** | Despacho, petições de quesitos, contestação do ente público (transcrever literal) |

### Passo 3 — Montar o JSON

Salve em `/tmp/prelaudo_med_[numero].json`:

```json
{
  "numero_processo": "",
  "vara_completa": "Vara da Família, Infância, Juventude, Idosos, Órfãos e Sucessões da Comarca de Jaraguá do Sul",
  "data_atual": "15 de Junho de 2026",
  "autores": ["Nome do autor"],
  "reus": ["Estado de Santa Catarina", "Município de ..."],
  "data_local_pericia": "Perícia ocorrida no dia ..., à ..., no ...",
  "presentes": [
    "Periciado: Nome – RG ...",
    "Acompanhante: Nome (parentesco) – RG ..."
  ],
  "historico": "...",
  "pedido": "Medicamento (nome e dose)",
  "antecedentes_familiares": "",
  "periciado_idade": "",
  "atestados": [
    {"data": "11/06/25", "motivo": "Relatório Médico", "medico": "Dra. ...", "folha": "20"}
  ],
  "exames": [
    {"data": "09/05/24", "exame": "TC Abdômen", "folha": "31", "conclusao": "..."}
  ],
  "quesitos_juizo": [],
  "quesitos_autor": [],
  "quesitos_reu": [
    {"numero": "1", "enunciado": "A parte autora já foi encaminhada para atendimento em órgão credenciado (CACON/UNACON)? ..."}
  ],
  "alertas": [
    "Exame físico, Discussão/Conclusão (incl. literatura) e respostas aos quesitos ficam em branco para após a perícia.",
    "Quesitos transcritos dos autos; quando não houver, registrados como não localizados."
  ]
}
```

Notas:
- `reus` aceita um ou dois entes (Estado e Município); os rótulos viram "1º Réu:", "2º Réu:".
- `quesitos_reu` recebe os quesitos do ente público (Estado e/ou Município) transcritos. Se Estado e Município tiverem conjuntos distintos, transcrever ambos em sequência.
- `atestados: []` ou `exames: []` removem a tabela e o título da subseção.
- `antecedentes_familiares` em branco quando não constar (é colhido na anamnese da perícia).

### Passo 4 — Gerar o ODT

```bash
python3 ~/.claude/scripts/gerar_prelaudo_medicamentos.py /tmp/prelaudo_med_[numero].json /tmp/PreLaudo_[numero].odt
```

Valide (`unzip -t`) e, para conferência visual, converta com LibreOffice headless e renderize as páginas.

### Passo 5 — Salvar na subpasta dos autos

Salvar como `PreLaudo_[numero do processo]_[NOME DO AUTOR].odt` (SEMPRE inclua o nome do autor/periciado extraído dos autos) na MESMA subpasta do Google Drive. Em sessão interativa, confirmar antes de salvar; na automação noturna autorizada, salvar direto.

Antes de dar o pré-laudo como pronto, rode SEMPRE o subagente `revisor-laudo` sobre o ODT e corrija o que ele apontar (repita até o veredito PRONTO). Etapa obrigatória, nunca pular.

---

## Localização dos arquivos

| Arquivo | Caminho |
|---|---|
| Gerador ODT (medicamentos) | `~/.claude/scripts/gerar_prelaudo_medicamentos.py` |
| Gerador ODT (previdenciário, reusado p/ estilos) | `~/.claude/scripts/gerar_prelaudo.py` |
| Template base (estilos) | `~/.claude/scripts/template_base.odt` |
| Laudos-modelo de medicamentos | `/Users/franciscolino/OneDrive/01 /TREINO IA/EXEMPLO MEDICAMENTOS/` |
| JSON temporário | `/tmp/prelaudo_med_[numero].json` |
| ODT gerado | `/tmp/PreLaudo_[numero].odt` |
