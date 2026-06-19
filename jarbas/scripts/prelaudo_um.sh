#!/bin/bash
# Gera o pré-laudo de UM processo (pasta dos autos passada como $1), via Claude headless.
# Usado tanto pelo agendador noturno (rodar_prelaudos.sh) quanto em testes pontuais.
set -uo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

SUB="${1:?uso: prelaudo_um.sh \"<pasta do processo>\"}"
CLAUDE="/usr/local/bin/claude"
LOGDIR="$HOME/.claude/logs"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/prelaudo_auto.log"
log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }

nome="$(basename "$SUB")"

# Roteamento por tipo (lê a capa do MAIOR PDF = os autos):
#   - interdição / curatela          -> skill jarbas-interdicao   (gerar_prelaudo_interdicao.py)
#   - medicamentos / procedimentos   -> skill jarbas-medicamentos (gerar_prelaudo_medicamentos.py)
#   - previdenciária do INSS         -> skill jarbas-pre-laudo     (gerar_prelaudo.py)
#   - outro tipo                     -> PULADO (sem skill própria; não gasta tokens)
# Ordem importa: interdição primeiro; medicamentos exige réu ente público + termo de saúde
# (cível/família se sobrepõem entre os tipos, por isso o roteamento é por conteúdo, não por vara).
PDF_CAPA=$(ls -S "$SUB"/*.[pP][dD][fF] 2>/dev/null | head -1)
TIPO=""
if [ -n "$PDF_CAPA" ]; then
  CAPA=$(python3 - "$PDF_CAPA" <<'PY'
import fitz,sys
try:
    d=fitz.open(sys.argv[1]); print("".join(d[i].get_text() for i in range(min(4,d.page_count)))[:5000])
except Exception: pass
PY
)
  # Ordem por especificidade do RÉU (o réu é o melhor discriminador). "Estado de Santa
  # Catarina" aparece no endereçamento de TODO laudo, então NÃO serve de chave sozinho;
  # medicamentos usa termos específicos da ação de saúde (Município/RENAME/CONITEC/fornecimento).
  if printf '%s' "$CAPA" | grep -qiE "interdi[çc][ãa]o|curatela|interditand|capacidade civil"; then
    TIPO="interdicao"
  elif printf '%s' "$CAPA" | grep -qiE "Seguradora|Seguros\b|Companhia de Seguros|Cia\.? de Seguros|Vida e Previd[êe]ncia|Seguros e Previd[êe]ncia|Previd[êe]ncia Privada|SUSEP|DPVAT|seguro de vida|seguro prestamista|Seguro, *(Contratos|Esp[ée]cies de contrato)"; then
    TIPO="securitaria"
  elif printf '%s' "$CAPA" | grep -qiE "Munic[íi]pio de|Secretaria de Estado da Sa[úu]de|RENAME|CONITEC|fornecimento de medicament|dispensa[çc][ãa]o de medicament|libera[çc][ãa]o d[eo]s? medicament|obriga[çc][ãa]o de fazer"; then
    TIPO="medicamentos"
  elif printf '%s' "$CAPA" | grep -qiE "INSTITUTO NACIONAL DO SEGURO SOCIAL|INSS|aux[íi]lio-(acidente|doen[çc]a)|benef[íi]cio por incapacidade|acidentes? de trabalho|Previd[êe]ncia Social"; then
    TIPO="previdenciario"
  fi
fi

if [ -z "$TIPO" ]; then
  log "PULADO (tipo não suportado por nenhuma skill do JARBAS — nem previdenciário nem interdição): $nome"
  exit 0
fi

if [ "$TIPO" = "interdicao" ]; then
  PROMPT="Gere o pré-laudo de INTERDIÇÃO/CURATELA do processo cujos autos (PDF) estão na pasta \"$SUB\". Você é o agente JARBAS na skill jarbas-interdicao. Siga rigorosamente as memórias prelaudo-interdicao, prelaudo-config-final e feedback-nunca-inventar. Passos: o MAIOR PDF da pasta são os autos; PDFs menores são exames/laudos avulsos a incorporar. Leia os PDFs com pymupdf (extraia o texto e renderize como imagem as páginas escaneadas — atestados, prontuários, exames, laudos); localize o despacho do juiz (data/hora/local da perícia) e os quesitos do juízo, da parte autora e do interditando, que podem estar em eventos posteriores do mesmo PDF; extraia os dados; monte o JSON em /tmp (campos autores[], interditandos[], presentes[], historico, atestados[], exames[], quesitos_juizo/autor/interditando, interditando_idade, alertas[]); gere o ODT com 'python3 ~/.claude/scripts/gerar_prelaudo_interdicao.py'; e salve PreLaudo_<numero do processo>.odt NA MESMA pasta \"$SUB\". O periciado é o INTERDITANDO. Deixe em branco o exame do estado mental, a Discussão/Conclusão e as respostas aos quesitos. quesitos_juizo vazio usa o conjunto fixo a-g (confira na decisão e registre observação). Nomes em caixa normal (exceção: a linha 'AO JUÍZO DA' em maiúsculas). Sempre registrar observações nas dúvidas. NÃO faça perguntas; trabalhe de forma autônoma. Ao final valide a integridade do ODT (unzip -t) e escreva um resumo de uma linha."
elif [ "$TIPO" = "medicamentos" ]; then
  PROMPT="Gere o pré-laudo de LIBERAÇÃO DE MEDICAMENTO/PROCEDIMENTO do processo cujos autos (PDF) estão na pasta \"$SUB\". Você é o agente JARBAS na skill jarbas-medicamentos. Siga rigorosamente as memórias prelaudo-medicamentos, prelaudo-config-final e feedback-nunca-inventar. Passos: o MAIOR PDF da pasta são os autos; PDFs menores são exames/laudos avulsos a incorporar. Leia os PDFs com pymupdf (extraia o texto e renderize como imagem as páginas escaneadas); localize o despacho do juiz (data/hora/local da perícia) e os quesitos do juízo, da parte autora e do(s) réu(s) (Estado/Município), que podem estar em eventos posteriores do mesmo PDF; extraia os dados; monte o JSON em /tmp (campos autores[], reus[], presentes[], historico, pedido, antecedentes_familiares, atestados[], exames[], quesitos_juizo/autor/reu, periciado_idade, alertas[]); gere o ODT com 'python3 ~/.claude/scripts/gerar_prelaudo_medicamentos.py'; e salve PreLaudo_<numero do processo>.odt NA MESMA pasta \"$SUB\". O réu é ente público (Estado de Santa Catarina e/ou Município). Transcreva os quesitos LITERALMENTE dos autos; NÃO pré-carregue nenhum conjunto; quando não houver, deixe vazio (vira 'não localizados'). Deixe em branco o Exame físico, a Discussão/Conclusão (inclusive a literatura sobre doença e medicamento) e as respostas aos quesitos. Nomes em caixa normal (exceção: a linha 'AO JUÍZO DA' em maiúsculas). Sempre registrar observações nas dúvidas. NÃO faça perguntas; trabalhe de forma autônoma. Ao final valide a integridade do ODT (unzip -t) e escreva um resumo de uma linha."
elif [ "$TIPO" = "securitaria" ]; then
  PROMPT="Gere o pré-laudo SECURITÁRIO (seguro / invalidez por acidente pessoal) do processo cujos autos (PDF) estão na pasta \"$SUB\". Você é o agente JARBAS na skill jarbas-securitaria. Siga rigorosamente as memórias prelaudo-securitaria, prelaudo-config-final e feedback-nunca-inventar. Passos: o MAIOR PDF da pasta são os autos; PDFs menores são exames/laudos avulsos a incorporar. Leia os PDFs com pymupdf (extraia o texto e renderize como imagem as páginas escaneadas); localize o despacho do juiz (data/hora/local da perícia) e os quesitos do juízo, da parte autora e do réu (a SEGURADORA), que podem estar em eventos posteriores do mesmo PDF; extraia os dados; monte o JSON em /tmp (campos autores[], reus[], presentes[], historico, pedido, atestados[], exames[], quesitos_juizo/autor/reu, autor_idade, alertas[]); gere o ODT com 'python3 ~/.claude/scripts/gerar_prelaudo_securitaria.py'; e salve PreLaudo_<numero do processo>.odt NA MESMA pasta \"$SUB\". O réu é seguradora privada (ex.: Icatu Seguros S/A). Pedido em geral 'Complementação da indenização'. Em Presentes inclua o Assistente Técnico da seguradora quando houver. Transcreva os quesitos LITERALMENTE; se a seguradora reproduzir a tabela SUSEP, NÃO reproduza a tabela inteira no pré-laudo, apenas registre uma observação de que ela foi juntada. Deixe em branco o Exame físico, a Discussão/Conclusão (graduação SUSEP) e as respostas aos quesitos. Nomes em caixa normal (exceção: a linha 'AO JUÍZO DA' em maiúsculas). Sempre registrar observações nas dúvidas. NÃO faça perguntas; trabalhe de forma autônoma. Ao final valide a integridade do ODT (unzip -t) e escreva um resumo de uma linha."
else
  PROMPT="Gere o pré-laudo do processo cujos autos (PDF) estão na pasta \"$SUB\". Você é o agente JARBAS na skill jarbas-pre-laudo. Siga rigorosamente as memórias prelaudo-config-final e feedback-nunca-inventar. Passos: o MAIOR PDF da pasta são os autos; eventuais PDFs menores são exames/laudos avulsos que devem ser incorporados na seção de exames. Leia os PDFs usando pymupdf (extraia o texto e renderize como imagem as páginas escaneadas — atestados, prontuários, exames, laudos — para lê-las); localize também o despacho do juiz (data/hora/local da perícia) e os quesitos do juízo, do autor e do réu, que podem estar em eventos posteriores do mesmo PDF; extraia todos os dados; monte o JSON em /tmp; gere o ODT com 'python3 ~/.claude/scripts/gerar_prelaudo.py'; e salve o arquivo PreLaudo_<numero do processo>.odt NA MESMA pasta \"$SUB\". Nome do autor e demais dados em caixa normal (exceção: a linha 'AO JUÍZO DA' em maiúsculas). Histórico sintético no formato aprovado. Sempre registrar observações para o perito nas dúvidas. NÃO faça perguntas; trabalhe de forma totalmente autônoma. Ao final, valide a integridade do ODT (unzip -t) e escreva um resumo de uma linha."
fi

log ">>> [um] Gerando pré-laudo ($TIPO): $nome"
TMPOUT=$(mktemp)

# Limite de tempo por processo (watchdog): se o Claude travar (ex.: Mac dormiu e perdeu
# a conexão, "ConnectionRefused"), encerra após TIMEOUT_S para não bloquear a noite toda.
TIMEOUT_S=1500   # 25 min; uma geração normal leva ~6-12 min
"$CLAUDE" -p "$PROMPT" --dangerously-skip-permissions > "$TMPOUT" 2>&1 &
cpid=$!
( sleep "$TIMEOUT_S"; kill -0 "$cpid" 2>/dev/null && { echo "[watchdog] tempo excedido (${TIMEOUT_S}s) — encerrando processo travado" >> "$TMPOUT"; kill -TERM "$cpid" 2>/dev/null; sleep 5; kill -KILL "$cpid" 2>/dev/null; } ) &
wdog=$!
wait "$cpid"; rc=$?
kill "$wdog" 2>/dev/null; wait "$wdog" 2>/dev/null
cat "$TMPOUT" >> "$LOG"

# Limite de cota/sessão: nenhum ODT é gravado, então o processo segue pendente.
# Devolvemos rc=99 e a hora do reset (RESET_EPOCH) para o worker pausar e retomar.
if grep -qiE "session limit|usage limit|hit your .*limit|reached your .*limit" "$TMPOUT"; then
  reset_epoch=$(python3 - "$TMPOUT" <<'PY'
import re,sys,datetime
txt=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'resets\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)', txt, re.I)
if not m: sys.exit(0)
h=int(m.group(1)); mm=int(m.group(2) or 0); ap=m.group(3).lower()
if ap=='pm' and h!=12: h+=12
if ap=='am' and h==12: h=0
now=datetime.datetime.now()
t=now.replace(hour=h,minute=mm,second=0,microsecond=0)
if t<=now: t+=datetime.timedelta(days=1)
print(int(t.timestamp()))
PY
)
  rm -f "$TMPOUT"
  log "<<< [um] LIMITE de cota atingido em: $nome (segue pendente; aguardando reset)"
  echo "RESET_EPOCH=${reset_epoch:-0}"
  exit 99
fi
rm -f "$TMPOUT"
if [ "$rc" -eq 0 ]; then log "<<< [um] OK: $nome"; else log "<<< [um] ERRO (rc=$rc): $nome"; fi
exit $rc
