---
name: jarbas-completar
description: Completa um laudo/pré-laudo ODT já pronto com exames e documentos trazidos na perícia, sem mexer no resto.
---

# Skill: /jarbas-completar — JARBAS: Completar laudo com documentos da perícia

> Skill do agente **JARBAS** (ver `/jarbas`). NÃO gera pré-laudo. Completa um laudo/pré-laudo ODT já pronto com exames e documentos que o autor trouxe NA perícia (não constavam nos autos).

## Papel

Após a perícia, o autor frequentemente apresenta exames ou documentos que não estavam nos autos. Esta skill lê a imagem (JPG/foto/PDF) de cada documento, extrai os dados e os insere nas tabelas certas do laudo ODT já existente, sem alterar nada do que o perito já preencheu (exame físico, discussão, quesitos).

Inputs: o laudo ODT do JARBAS (`PreLaudo_*.odt`) e uma ou mais imagens dos documentos.
Destino: as tabelas **Atestados e Declarações** e **Exames complementares** do mesmo laudo.

## Regras absolutas

- NUNCA inventar. Transcrever a conclusão do exame LITERALMENTE da imagem. Se algo estiver ilegível, transcrever o que der e registrar a dúvida ao usuário.
- Classificar cada documento: exame de imagem/laboratório/anatomopatológico com conclusão → tabela de Exames; relatório/atestado/declaração/laudo médico → tabela de Atestados e Declarações.
- A coluna "Nº Folha" desses documentos recebe **"Apresentado na perícia"** (não constam dos autos), salvo orientação diferente do usuário.
- Confirmar com o usuário o que foi extraído ANTES de inserir e salvar.
- Nunca sobrescrever o laudo original sem confirmação; por padrão gerar um novo arquivo `PreLaudo_<numero>_completo.odt`.

---

## Fluxo de execução

### Passo 1 — Localizar os arquivos
O usuário indica o laudo ODT e as imagens dos documentos (em geral na mesma subpasta do processo na pasta do Google Drive, ou caminhos que ele informar).

### Passo 2 — Ler cada imagem (visão)
Para cada JPG/imagem, leia com a ferramenta Read (visão). Extraia:
- **Exame:** data, tipo do exame e a CONCLUSÃO (transcrição literal).
- **Atestado/relatório/declaração:** data, motivo/tipo e médico.
Se a imagem for um PDF escaneado, renderize a página com pymupdf (dpi 170-200) e leia o PNG.

### Passo 3 — Classificar e montar o JSON
Monte `/tmp/dados_novos_[numero].json`:

```json
{
  "exames": [
    {"data": "10/06/26", "exame": "PET-CT Oncológico", "folha": "Apresentado na perícia", "conclusao": "..."}
  ],
  "atestados": [
    {"data": "09/06/26", "motivo": "Relatório do oncologista", "medico": "Dra. ...", "folha": "Apresentado na perícia"}
  ]
}
```

### Passo 4 — Confirmar com o usuário
Mostre o que foi extraído de cada documento (data, tipo, médico, conclusão) e em qual tabela vai entrar. Só prossiga após o "ok".

### Passo 5 — Inserir no laudo

```bash
python3 ~/.claude/scripts/completar_laudo.py \
  "/caminho/PreLaudo_<numero>.odt" \
  /tmp/dados_novos_[numero].json \
  "/caminho/PreLaudo_<numero>_completo.odt"
```

O script acrescenta as linhas às tabelas existentes; se o laudo não tinha a tabela de Atestados ou de Exames (porque não havia nada nos autos), ele recria a subseção (4.1/4.2) com a numeração e a formatação corretas, sem tocar no restante.

### Passo 6 — Validar e entregar
Valide a integridade (`unzip -t`). Para conferência, converta com LibreOffice headless e renderize a página dos Documentos. Informe o caminho do arquivo completado. Substituir o original somente com confirmação do usuário.

---

## Como funciona o script (CIENTE DE ESTILO)

`~/.claude/scripts/completar_laudo.py laudo_entrada.odt dados_novos.json laudo_saida.odt`
- Funciona tanto nos **laudos Word do Dr.** (numeração/estilos próprios, ex.: Table5 = exames) quanto nos **ODT gerados pelo JARBAS** — porque localiza as tabelas pelo CABEÇALHO (Exames: tem "EXAME"+"Folha"; Atestados: tem "MOTIVO"+"MÉDICO"), não pelo nome/numeração.
- Clona os ESTILOS do próprio documento (linha-modelo existente), em vez de impor estilos fixos.
- Exames: se houver uma linha-modelo em branco + "CONCLUSÃO:" (padrão do modelo Word), ela é preenchida no lugar; senão, clona o par (dados + CONCLUSÃO) e acrescenta. A CONCLUSÃO aceita múltiplos parágrafos via `\n`.
- Atestados: clona a última linha de dados e acrescenta.
- DEDUP: pula documento cujo nome (exame) ou motivo já conste na tabela — assim rodar duas vezes não duplica. Relata "nada a inserir (já presentes)".
- Preserva tudo o mais (exame físico, discussão, quesitos já respondidos pelo perito).

## Atenção ao localizar os arquivos (OneDrive / acentos)

- Caminhos no OneDrive podem usar acentos em normalização NFD (≠ do que digito em NFC); por isso caminho digitado com acento pode dar "No such file". SEMPRE localizar os arquivos navegando por `os.listdir` + correspondência por SUBSTRING sem acento (ex.: "PAUTA", "ADILSON", "LAUDO"), não por caminho digitado.
- As pastas da pauta podem ser RENOMEADAS após a perícia (ex.: cai o prefixo de horário e o sufixo " ok"). Localizar pela parte estável do nome (o nome do periciado).

## Localização dos arquivos

| Arquivo | Caminho |
|---|---|
| Script | `~/.claude/scripts/completar_laudo.py` |
| Gerador base (estilos/tabelas reusados) | `~/.claude/scripts/gerar_prelaudo.py` |
| JSON temporário | `/tmp/dados_novos_[numero].json` |
| Laudo completado | `PreLaudo_<numero>_completo.odt` (na pasta do processo) |
