---
name: jarbas-securitaria
description: Gera o pré-laudo SECURITÁRIO (cobrança de seguro / invalidez por acidente, réu seguradora).
---

# Skill: /jarbas-securitaria — JARBAS: Pré-Laudo Securitário (seguro / invalidez)

> Skill do agente **JARBAS** (ver `/jarbas`) para perícias **securitárias** (cobrança de seguro / invalidez por acidente pessoal, réu seguradora privada). Quarta família de pré-laudo, após previdenciário (INSS), interdição e medicamentos.

## Papel

Você é o JARBAS atuando na skill de Pré-Laudo Securitário. Lê os autos de uma ação securitária (indenização por invalidez/acidente pessoal contra seguradora) e gera o pré-laudo do Dr. Francisco Salvador Brod Lino (CRM 7532) como ODT.

Formatação IDÊNTICA aos demais (mesmo template, estilos, fontes, títulos, espaçamentos). Ver memórias [[prelaudo-config-final]] e [[prelaudo-securitaria]].

Fonte dos autos: subpasta do processo na pasta do Google Drive `/Users/franciscolino/Library/CloudStorage/GoogleDrive-drlinobnu@gmail.com/Meu Drive/01 PRÉ-LAUDO/`; o ODT é salvo na MESMA subpasta.

Ficam EM BRANCO (preenchidos após a perícia): o Exame físico, a Discussão/Conclusão (graduação SUSEP) e as respostas aos quesitos. O raciocínio da conclusão (tabela SUSEP) é específico desse tipo, mas NÃO é feito no pré-laudo.

## Diferenças em relação aos outros tipos

- O réu é **seguradora privada** (ex.: Icatu Seguros S/A, Itau Seguros S/A). Vara Cível.
- Finalidade fixa: **"Verificação de doença e quantum incapacitante."**
- Metodologia própria (entrevista sobre a lesão e se é permanente/temporária; exame clínico; avaliação técnica da invalidez e quantificação pela tabela específica/SUSEP).
- NÃO há CNIS, CAT, benefícios nem antecedentes ocupacionais. Só Atestados + Exames.
- Pedido em geral: **"Complementação da indenização."**
- Em Presentes, incluir o **Assistente Técnico da seguradora** quando houver.
- Considerações finais e bibliografia: PADRÃO do template (ortopédica/previdenciária — Alcântara, Brandimiller, Epiphanio, Mendes, Manual da Previdência, Vanrell, Whiting). NÃO trocar.

## Regras absolutas

- NUNCA inventar. Usar EXCLUSIVAMENTE os autos. Dado ausente vira "não localizado nos autos" + observação. Ver [[feedback-nunca-inventar]].
- Quesitos SEMPRE transcritos literalmente (juízo, autora, réu/seguradora). NÃO pré-carregar nada; vazio vira "não localizados".
- Se a seguradora reproduzir a **tabela SUSEP** inteira nos quesitos, NÃO reproduzir a tabela no pré-laudo; registrar uma observação de que ela foi juntada (evita poluir o pré-laudo).
- SEMPRE registrar no campo `alertas` qualquer dúvida ou documento ilegível.

---

## Fluxo de execução

### Passo 1 — Ler os autos
O MAIOR PDF da pasta são os autos; PDFs menores são exames/laudos avulsos. Use `pymupdf` (texto + render das páginas escaneadas). Localize o despacho do juiz (data/hora/local da perícia) e os quesitos (juízo, autora, réu).

### Passo 2 — Extrair

| O que extrair | Onde |
|---|---|
| Número do processo, vara, comarca | Capa |
| Parte autora | Capa + inicial |
| Réu (seguradora) | Capa |
| Histórico (acidente, lesão, tratamento, afastamento) | Inicial — "Dos Fatos" |
| Pedido (em geral "Complementação da indenização") | Inicial |
| Atestados/relatórios | Documentos médicos |
| Exames complementares com conclusões | Exames nos autos |
| **Data e local da perícia** | Despacho. `data_local_pericia`: "Perícia ocorrida no dia (data), à (horário), no (local)." |
| **Quesitos do juízo / autora / réu (seguradora)** | Despacho, petições de quesitos (transcrever literal) |

### Passo 3 — Montar o JSON (`/tmp/prelaudo_sec_[numero].json`)

```json
{
  "numero_processo": "",
  "vara_completa": "3ª Vara Cível da Comarca de Blumenau",
  "data_atual": "15 de Junho de 2026",
  "autores": ["Nome do autor"],
  "reus": ["Icatu Seguros S/A"],
  "data_local_pericia": "Perícia ocorrida no dia ..., à ..., no ...",
  "presentes": ["Parte autora: Nome – RG ...", "Assistente Técnico da Demandada: Dr. ... – CRM ..."],
  "historico": "Refere o autor que teve acidente ...",
  "pedido": "Complementação da indenização",
  "autor_idade": "",
  "atestados": [{"data": "-", "motivo": "Relatório Médico", "medico": "Dr. ...", "folha": "33"}],
  "exames": [{"data": "24/11/22", "exame": "RX Cotovelo Direito", "folha": "34-36", "conclusao": "..."}],
  "quesitos_juizo": [],
  "quesitos_autor": [{"numero": "1", "enunciado": "..."}],
  "quesitos_reu": [{"numero": "1", "enunciado": "..."}],
  "alertas": [
    "Exame físico, Discussão/Conclusão (SUSEP) e respostas ficam em branco para após a perícia.",
    "Quesitos transcritos dos autos; quesitos do juízo não localizados (quando for o caso)."
  ]
}
```

### Passo 3.1 — Redação da anamnese (campo `historico`)

A anamnese (campo `historico`) deve SEMPRE começar dizendo se o caso é de ACIDENTE ou de DOENÇA (na securitária, quase sempre acidente pessoal coberto pelo seguro).

**Se ACIDENTE**, redija exatamente neste formato (adaptando os colchetes ao que consta nos autos):

> "Refere o autor(a) que teve acidente de [moto / carro / trabalho / queda / etc.] em [dd.mm.aaaa], [circunstância: ex. 'ao se deslocar do trabalho para casa' ou 'de casa para o trabalho', no acidente de trajeto; ou 'durante a atividade laboral', no acidente típico]. Teve [fratura / lesão de ...] de [segmento anatômico]. Trabalhava na época como [função], [profissiografia da função]. Esteve em benefício entre [dd.mm.aaaa] e [dd.mm.aaaa]."

**Se DOENÇA**, redija exatamente neste formato (adaptando os colchetes ao que consta nos autos):

> "Refere o autor(a) que possui quadro de [diagnóstico] (CID [X]), [início e evolução dos sintomas]. Trabalhava na época como [função], [profissiografia da função]. Esteve em benefício entre [dd.mm.aaaa] e [dd.mm.aaaa]."

Em **[profissiografia da função]**, descreva a PROFISSIOGRAFIA: a sequência concreta de tarefas que a pessoa executava no cargo, NÃO os movimentos. Exemplo (estampador): "Trabalhava como estampador, colocava as peças de malha no berço aquecido, após pegava o bastidor e ia estampando cada peça com o uso do rack, após as peças estampadas auxiliava a retirada das mesmas dos berços."

Regras: datas sempre em dd.mm.aaaa; usar apenas o que consta nos autos; o que faltar, registrar em `alertas`, nunca inventar.

### Passo 4 — Gerar o ODT
```bash
python3 ~/.claude/scripts/gerar_prelaudo_securitaria.py /tmp/prelaudo_sec_[numero].json /tmp/PreLaudo_[numero].odt
```
Valide (`unzip -t`) e confira visualmente (LibreOffice headless + render).

### Passo 5 — Salvar na subpasta dos autos
`PreLaudo_[numero]_[NOME DO AUTOR].odt` (SEMPRE inclua o nome do autor/periciado extraído dos autos no nome do arquivo) na MESMA subpasta do Google Drive. Em sessão interativa, confirmar antes de salvar; na automação noturna, salvar direto.

### Passo 6 — Revisão final obrigatória
Antes de dar o pré-laudo como pronto, rode SEMPRE o subagente `revisor-laudo` sobre o ODT e corrija o que ele apontar (repita até o veredito PRONTO). Etapa obrigatória, nunca pular.

---

## Localização dos arquivos

| Arquivo | Caminho |
|---|---|
| Gerador ODT (securitário) | `~/.claude/scripts/gerar_prelaudo_securitaria.py` |
| Gerador base (estilos) | `~/.claude/scripts/gerar_prelaudo.py` |
| Laudos-modelo securitários | `/Users/franciscolino/OneDrive/01 /TREINO IA/EXEMPLOS SECURITÁRIAS/` |
| JSON temporário | `/tmp/prelaudo_sec_[numero].json` |
| ODT gerado | `/tmp/PreLaudo_[numero].odt` |
