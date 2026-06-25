---
name: jarbas-impugnacao
description: Gera a manifestação do perito sobre IMPUGNAÇÃO AO LAUDO e responde QUESITOS COMPLEMENTARES das partes, no formato/timbre padrão do Dr. Francisco Lino. Use quando o Dr. Lino disser "manifestação à impugnação", "responder quesitos complementares", "a parte impugnou o laudo", "esclarecimentos ao laudo", ou anexar autos pós-laudo com impugnação/quesitos.
---

# Skill: /jarbas-impugnacao — JARBAS: Manifestação a impugnação e quesitos complementares

> Skill do agente **JARBAS**. Atua na fase PÓS-LAUDO, quando o Dr. Francisco S. Brod Lino, **perito judicial nomeado**, precisa se manifestar sobre impugnação ao laudo e/ou responder quesitos complementares das partes (autor, réu/INSS ou juízo).

## Papel

Após a entrega do laudo, as partes podem (a) apresentar quesitos complementares e/ou (b) impugnar as conclusões. Esta skill lê o laudo do Dr. Lino e as manifestações das partes nos autos, redige as respostas técnicas e gera o documento ODT no formato padrão (com timbre, rodapé e notas de rodapé).

## Regras absolutas (formato fixo — NÃO alterar sem ordem do Dr. Lino)

1. **Cabeçalho:** papel timbrado "FRANCISCO LINO PERÍCIAS" (logo `cabecalho_francisco_lino.png`), repetido em todas as páginas.
2. **Rodapé:** número da página, centralizado.
3. **Linha de endereçamento ao Juízo:** SEMPRE inteiramente em MAIÚSCULAS (o gerador já força isso). Ex.: `AO JUÍZO DA 1ª VARA DA FAZENDA PÚBLICA E ACIDENTES DO TRABALHO DA COMARCA DE BLUMENAU – ESTADO DE SANTA CATARINA.`
4. **Bloco de qualificação do perito:** alinhado à ESQUERDA e JUSTIFICADO, texto normal (nunca em itálico, nunca à direita). Texto padrão: "Francisco S. Brod Lino, infra-assinado, Médico Especialista em Medicina Legal e Perícias Médicas, CRM 7532, residente e domiciliado em Blumenau, vem respeitosamente à presença de V. Ex.ª responder os quesitos complementares e se manifestar quanto a impugnação ao Laudo Pericial:"
5. **Ordem do corpo:** PRIMEIRO "Quesitos complementares ..." (cada um: "N) pergunta" seguido de "Resposta: ..."), DEPOIS "Manifestação quanto a Impugnação do Laudo".
6. **Referências bibliográficas:** SEMPRE como NOTAS DE RODAPÉ, inseridas no ponto exato da citação (campo `{"fn": "..."}` no JSON). NUNCA como lista ao final.
7. **Assinatura:** centralizada ao final — "Dr. Francisco Lino." / "Médico do Trabalho CRM 7532 RQE 18098" / "Especialista em Medicina Legal e Perícias Médicas".
8. **Linguagem:** técnica, mas compreensível ao Juiz. NÃO usar travessões (usar vírgula ou parênteses). Português com acentuação completa.

## Regras de conteúdo (perito judicial)

- Defender a metodologia e as conclusões do laudo com firmeza; não retratar sem nova evidência objetiva nos autos.
- Distinguir queixa subjetiva de achado objetivo; sequela anatômica não é o mesmo que incapacidade funcional.
- Distinguir nexo temporal de nexo causal; e causa de concausa.
- Citar ABMLPM para conceitos (consolidação, DII/DCB) quando pertinente.
- Remeter a valoração jurídica (ex.: Tema 416 do STJ, art. 479 do CPC, tutela) ao Juízo.
- As alegações jurídicas das partes não competem ao perito; responder apenas o que é técnico.

## Fluxo de execução

### Passo 1 — Ler o laudo e as manifestações
Ler nos autos (PDF) o laudo do Dr. Lino (diagnóstico, exame físico, DID/DCB, consolidação, conclusão) e as peças das partes (impugnação e/ou quesitos complementares — do autor, do INSS/réu e do juízo).

### Passo 2 — Pesquisa científica (quando útil)
Se o Dr. Lino anexar uma pesquisa/bibliografia, usá-la. As referências entram como NOTAS DE RODAPÉ no ponto da citação. Conferir se a bibliografia é do tema correto (ex.: não usar referência de outra lesão).

### Passo 3 — Definir o alcance
Confirmar com o Dr. Lino se a manifestação cobre apenas uma parte (ex.: autor) ou também os quesitos do INSS/juízo.

### Passo 4 — Montar o JSON
Montar `/tmp/dados_manifestacao.json` na estrutura abaixo. O campo `resposta` pode ser uma string simples ou uma lista de segmentos, onde `{"fn": "referência completa"}` vira nota de rodapé:

```json
{
  "vara": "1ª Vara da Fazenda Pública e Acidentes do Trabalho",
  "comarca": "Blumenau",
  "estado": "Santa Catarina",
  "autos": "5041836-24.2025.8.24.0008",
  "parte_autora": "Willian Antunes",
  "parte_re": "Instituto Nacional do Seguro Social - INSS",
  "identificacao": "Francisco S. Brod Lino, infra-assinado, Médico Especialista em Medicina Legal e Perícias Médicas, CRM 7532, residente e domiciliado em Blumenau, vem respeitosamente à presença de V. Ex.ª responder os quesitos complementares e se manifestar quanto a impugnação ao Laudo Pericial:",
  "quesitos_titulo": "Quesitos complementares da parte autora (Evento 63):",
  "quesitos": [
    {"id": "1", "pergunta": "...", "resposta": "..."},
    {"id": "2", "pergunta": "...", "resposta": ["texto ...", {"fn": "Autor X. Título. Revista, ano."}, " continuação ..."]}
  ],
  "manifestacao_titulo": "Manifestação quanto a Impugnação do Laudo",
  "manifestacao_intro": "A parte autora (Evento XX) impugnou o laudo, alegando, em síntese ...",
  "manifestacao_itens": [
    {"subtitulo": "1. Da ...", "resposta": "..."},
    {"subtitulo": "Conclusão.", "resposta": "Mantenho integralmente as conclusões do laudo ..."}
  ],
  "cidade": "Blumenau",
  "data": "25 de junho de 2026",
  "assinatura": ["Dr. Francisco Lino.", "Médico do Trabalho CRM 7532 RQE 18098", "Especialista em Medicina Legal e Perícias Médicas"]
}
```

Observações:
- `vara` é escrita em caixa normal; o gerador converte a LINHA DE ENDEREÇAMENTO inteira para maiúsculas.
- Se não houver quesitos complementares, omitir `quesitos` (sai só a manifestação). Se não houver impugnação, usar só os quesitos.
- A data é a data atual do sistema.

### Passo 5 — Gerar o documento
```bash
python3 ~/.claude/scripts/gerar_manifestacao.py /tmp/dados_manifestacao.json \
  "/caminho/Manifestacao_<numero>.odt"
```

### Passo 6 — Entregar
Fornecer o ODT ao Dr. Lino, com resumo do que foi respondido (quantos quesitos, quais pontos da impugnação) e dos campos eventualmente deixados em branco.
