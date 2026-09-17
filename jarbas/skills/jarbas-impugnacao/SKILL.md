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

## Conferência factual e fundamentação (regras de 27 e 28.08.2026, caso Dorival e caso Natália)

- **Estrutura anatômica: só a que consta do documento.** Antes de usar qualquer argumento
  topográfico, localizar no PDF dos autos a hipótese diagnóstica EXATA registrada pelo médico
  assistente e pela perícia administrativa (buscar "suspeita", o CID e o nome da estrutura), nunca
  inferir a estrutura do CID genérico. No caso Dorival a manifestação dizia "ligamento cruzado
  anterior" e o laudo SABI registrava "posterior" (o CID S83.5 cobre os dois): o argumento apontava
  para a estrutura suspeitada e seria munição para a réplica. Se a topografia coincidir com a
  suspeita, descartar o argumento e sustentar pela manobra semiológica negativa (gaveta, Lachman).
- **A série de perícias do INSS é o filme; o exame pericial é o retrato.** Varrer TODAS as perícias
  administrativas do PDF: (a) a contemporânea ao acidente serve de linha de base para demonstrar a
  EVOLUÇÃO até o exame normal (marcha claudicante, edema, hipotrofia em 2021 contra exame normal em
  2026 é justamente o que responde à alegação de contradição); (b) as posteriores provam que o
  segmento não voltou a ser objeto de queixa. Citar sempre Evento, documento e página.
- **Método, tabela ou escala de terceiro invocado pela parte:** (1) baixar e ler a fonte primária
  citada nos autos antes de responder; (2) recusar o método com as palavras do próprio autor (o
  título "Proposta para a valoração..." e a conclusão que pede validação de reprodutibilidade), e
  não por argumento de autoridade; (3) tom cortês, nominando o autor com a grafia EXATA da
  publicação (é "Weliton Barbosa Santos", não "Wellington"; avisar o Dr. quando a grafia dele
  divergir); (4) fechar reafirmando a referência adotada (Tabela Brasileira da ABMLPM) e que a
  escolha do método é do perito. Ver memória feedback-refutar-metodo-da-parte-com-respeito.
- **Auxílio-acidente: retorno ao trabalho NÃO afasta a redução** (correção do Dr., 17.09.2026).
  Nas respostas a quesitos complementares e nas manifestações, nunca usar o retorno ao trabalho
  habitual, a permanência na mesma função ou empregador, a ausência de novo afastamento ou de
  readaptação como argumento para manter a negativa ou o grau mínimo da redução. O benefício
  indeniza quem segue trabalhando com maior dificuldade. A manutenção do laudo se sustenta no exame
  pericial, nas imagens, nos documentos contemporâneos e na literatura. Se a parte perguntar se o
  retorno demonstra ausência de redução, responder que, por si só, não demonstra. Detalhe na
  Regra 31 da /jarbas-conclusao.
- **Literatura em nota de rodapé:** conferir na fonte o segmento anatômico do estudo, a autoria e
  os achados desfavoráveis do mesmo resumo antes de gravar (Regra 27 da /jarbas-conclusao).
- **Campos de formulário do INSS (SABI, CAT, comunicação de decisão):** só se afirmam depois de
  ler a página como imagem; a extração de texto embaralha rótulo e valor (item 10 do Passo 3 da
  /jarbas-conclusao).

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
O script fica no diretório do plugin. Há também um symlink em `~/.claude/scripts/gerar_manifestacao.py` que aponta para ele (qualquer um dos dois caminhos funciona no laptop).
```bash
python3 ~/jarbas-plugin/jarbas/scripts/gerar_manifestacao.py /tmp/dados_manifestacao.json \
  "/caminho/Manifestacao_<numero>.odt"
```

### Passo 5.1 — Normalizar a FORMA (obrigatório, antes de entregar)

Vale sobretudo para as peças montadas sobre o modelo .doc/.odt que a secretária manda
(quesitos complementares e manifestações). Esse modelo tem quatro defeitos de forma que
NÃO aparecem na leitura do texto e que já voltaram três vezes da mesa do Dr.:

1. o estilo de parágrafo `Standard` vem em **Times New Roman** (a fonte é Arial); como todos
   os parágrafos do corpo declaram Arial por conta própria, o único que herda a serifa é o da
   qualificação do perito, e passa despercebido;
2. o número de página do rodapé vem em 9pt (o padrão é **Arial 10 negrito**);
3. o `style:dynamic-spacing` do cabeçalho engole a margem inferior e o texto **encosta na logo**
   nas páginas que começam no meio de um parágrafo (a página 1 fica boa, por isso engana);
4. a cada save no editor do Dr. o PNG do logo é descartado do pacote.

Rodar SEMPRE ao terminar as respostas, ANTES de entregar para revisão:

```bash
# PADRÃO (peça que sai com o timbre do Dr. Francisco Lino):
python3 ~/.claude/scripts/normalizar_peca_lino.py "<peça.odt>"

# só quando a peça tem de sair com o banner do modelo da secretária:
python3 ~/.claude/scripts/normalizar_peca_secretaria.py "<peça.odt>"
```

Desde 28.08.2026 o padrão é o `normalizar_peca_lino.py`. Ele reescreve o `<style:header>` na
estrutura canônica dos laudos do JARBAS (frame `as-char` dentro de um `text:p` Standard, `xlink:href`
completo, PNG no zip e entrada no manifest), que é a ÚNICA que sobrevive ao open/save do editor do
Dr.; deixa o vão abaixo da logo em 0,1 cm (`fo:min-height` = altura do frame + 0,093 cm), a margem
de topo em 1,016 cm e o rodapé em Arial 10 negrito. O `normalizar_peca_secretaria.py` continua para
as peças que devem manter o banner da secretária, que é outro PNG.

Conferir sempre no relatório: logo `sim` em TODAS as páginas e nenhuma fonte serifada no PDF.

Mais duas conferências de forma que o olho não pega (25.08 e 05.09.2026):

- **Linha atravessando a logo.** Os estilos de parágrafo do cabeçalho herdados do modelo (MP1, que
  ancora a logo, e MP2, o vazio seguinte) podem trazer `fo:border-bottom="0.004cm solid #000000"`;
  como a imagem é mais alta que a linha, a borda é desenhada no MEIO da logo e quase some sobre o
  azul. Zerar todo `fo:border` não intencional nos estilos do header e, na revisão, listar os
  vetores do PDF (`page.get_drawings()`, traços de altura zero na faixa do cabeçalho).
- **Timbre alinhado à margem do texto** (pedido do Dr., parecer GFE, 05.09.2026): o parágrafo que
  ancora a logo com `fo:text-align="start"` e o estilo do frame sem margens laterais (o molde
  centralizava com margem de 0,319 cm e a logo saía 0,3 cm à direita do texto). Correção só no
  styles.xml, para não perder edições de conteúdo do Dr.

O script corrige esses pontos, autocalibra o vão abaixo da logo em 0,8 cm medindo o PDF
renderizado, e imprime um relatório (folhas, logo por página, fontes em uso, margem acima da logo,
vão mínimo e máximo). Só concluir quando ele imprimir `OK`. Use `--conferir` para relatório sem
alterar nada.
Também aproxima a logo da borda superior da folha: o modelo vem com margem de topo de 1,249 cm e
passa para 0,70 cm (logo a 0,63 cm da borda), que é o padrão pedido pelo Dr. em 25.08.2026.


Ele mexe apenas em `styles.xml`, no manifesto e no PNG: **nunca abre o content.xml**. Por isso pode
ser reaplicado quantas vezes for preciso, inclusive depois de o Dr. ter editado o texto — e é
justamente o que se deve fazer, porque o save dele desfaz o ajuste do cabeçalho.

### Passo 6 — Entregar
Fornecer o ODT ao Dr. Lino, com resumo do que foi respondido (quantos quesitos, quais pontos da impugnação) e dos campos eventualmente deixados em branco. Informar também o resultado do Passo 5.1 (folhas, logo, fontes, vão). Se o Dr. devolver o arquivo com edições dele, rodar o Passo 5.1 de novo antes da entrega final.

O revisor-laudo passa o humanizer junto desde 25.08.2026 (Passo 5 do agente), apontando as marcas
de escrita de IA no texto do perito sem reescrever. Não é mais preciso pedir a humanização à parte;
quem aplica as reescritas sugeridas é a sessão principal.



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
