#!/bin/bash
# Automação JARBAS (skill jarbas-pre-laudo) — detecta processos pendentes e gera os pré-laudos faltantes.
# Uso: rodar_prelaudos.sh [check|run]   (default: run)
#   check = apenas verifica e registra as pendências (job das 20h)
#   run   = verifica e gera os pré-laudos pendentes (job noturno 22h-07h;
#           pausa e retoma se bater o limite de cota, esperando o reset)
# Roda localmente no Mac. A base dos autos/pré-laudos é o Google Drive para Desktop
# (Meu Drive/01 PRÉ-LAUDO) — manter a pasta marcada como "Disponível off-line".

set -uo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

MODE="${1:-run}"
# Mantém o Mac acordado enquanto a rotina roda (caffeinate encerra junto com este script).
# ATENÇÃO: em BATERIA o sistema ainda pode dormir; manter o Mac na TOMADA (AC) à noite.
caffeinate -dimsu -w $$ 2>/dev/null &
# Base única e configurável (editar em prelaudo_base.conf, não aqui):
BASE_CONF="$HOME/.claude/scripts/prelaudo_base.conf"
[ -f "$BASE_CONF" ] && source "$BASE_CONF"
PASTA="${PASTA:-/Volumes/Dados/Perícias e MED Trabalho/01PRÉ_LAUDO}"
CLAUDE="/usr/local/bin/claude"
DEADLINE_HOUR=7            # parar de iniciar novos processos a partir das 07h
MAX_PAUSAS=2               # nº máximo de pausas para esperar reset de cota por noite
LOGDIR="$HOME/.claude/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/prelaudo_auto.log"

log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# Trava de execução única no modo RUN (evita que a manual e a das 22h rodem juntas).
if [ "$MODE" = "run" ]; then
  LOCK="$LOGDIR/prelaudo_run.lock"
  if mkdir "$LOCK" 2>/dev/null; then
    echo $$ > "$LOCK/pid"; trap 'rm -rf "$LOCK"' EXIT
  else
    oldpid=$(cat "$LOCK/pid" 2>/dev/null || true)
    if [ -n "${oldpid:-}" ] && kill -0 "$oldpid" 2>/dev/null; then
      log "Já há um RUN em andamento (PID $oldpid). Esta execução sai sem fazer nada."
      exit 0
    fi
    rm -rf "$LOCK"; mkdir "$LOCK"; echo $$ > "$LOCK/pid"; trap 'rm -rf "$LOCK"' EXIT
    log "Lock órfão removido; assumindo a execução."
  fi
fi

log "===== Início ($MODE) ====="

if [ ! -d "$PASTA" ]; then
  log "ERRO: volume não montado ou pasta inacessível: $PASTA"
  log "(verifique se o Mac está ligado e o disco de rede montado)"
  exit 1
fi

# Sonda de acesso real: o teste -d passa mesmo sem permissão de leitura no volume.
# Sem isso, um 'Operation not permitted' do TCC viraria falso 'nenhum pendente'.
if ! ls "$PASTA" >/dev/null 2>&1; then
  log "ERRO: sem permissão para LER o volume (Acesso Total ao Disco ausente para o /bin/bash?): $PASTA"
  log "Conceda Acesso Total ao Disco ao /bin/bash em Ajustes do Sistema e tente novamente."
  exit 1
fi

# Detecta subpastas pendentes (têm PDF, não têm PreLaudo_*.odt)
pendentes=()
while IFS= read -r sub; do
  [ -d "$sub" ] || continue
  shopt -s nullglob nocaseglob
  pdfs=( "$sub"/*.pdf )
  odts=( "$sub"/PreLaudo_*.odt )
  shopt -u nullglob nocaseglob
  if [ ${#pdfs[@]} -gt 0 ] && [ ${#odts[@]} -eq 0 ]; then
    pendentes+=( "$sub" )
  fi
done < <(find "$PASTA" -mindepth 1 -maxdepth 1 -type d ! -name '.*')

if [ ${#pendentes[@]} -eq 0 ]; then
  log "Nenhum processo pendente. Encerrando."
  exit 0
fi

log "${#pendentes[@]} processo(s) pendente(s):"
for p in "${pendentes[@]}"; do log "   - $(basename "$p")"; done

if [ "$MODE" = "check" ]; then
  log "Modo verificação (20h): as pendências serão processadas na janela noturna (22h-07h)."
  exit 0
fi

# Modo run: gera os pré-laudos, parando se ultrapassar a janela noturna (07h).
# Se bater o limite de cota (rc=99), pausa até o reset e retoma de onde parou
# (quebra a rotina em duas/mais passagens, conforme a cota disponível).
pausas=0
i=0
while [ $i -lt ${#pendentes[@]} ]; do
  sub="${pendentes[$i]}"
  H=$(date '+%H'); H=${H#0}; [ -z "$H" ] && H=0
  if [ "$H" -ge "$DEADLINE_HOUR" ] && [ "$H" -lt 20 ]; then
    log "Janela noturna encerrada (>=${DEADLINE_HOUR}h). $(( ${#pendentes[@]} - i )) restante(s) ficam para a próxima noite."
    break
  fi

  out=$(bash "$HOME/.claude/scripts/prelaudo_um.sh" "$sub")
  rc=$?

  if [ "$rc" -eq 99 ]; then
    # Limite de cota atingido. O processo $sub NÃO foi gerado: não avança o índice.
    reset_epoch=$(printf '%s\n' "$out" | sed -n 's/^RESET_EPOCH=//p' | tail -1)
    now=$(date +%s)

    if [ "$pausas" -ge "$MAX_PAUSAS" ]; then
      log "Limite de cota atingido e nº máximo de pausas ($MAX_PAUSAS) já usado. Restantes ficam para a próxima noite."
      break
    fi
    if [ -z "$reset_epoch" ] || [ "$reset_epoch" -le "$now" ] 2>/dev/null; then
      log "Limite de cota atingido, mas não consegui ler o horário do reset. Restantes ficam para a próxima noite."
      break
    fi

    wake=$(( reset_epoch + 120 ))          # 2 min de folga após o reset
    wake_h=$(date -r "$wake" '+%H'); wake_h=${wake_h#0}; [ -z "$wake_h" ] && wake_h=0
    if [ "$wake_h" -ge "$DEADLINE_HOUR" ] && [ "$wake_h" -lt 20 ]; then
      log "Reset cairia às $(date -r "$wake" '+%H:%M'), fora da janela (>=${DEADLINE_HOUR}h). Restantes ficam para a próxima noite."
      break
    fi

    espera=$(( wake - now )); [ "$espera" -lt 0 ] && espera=0
    pausas=$(( pausas + 1 ))
    log "Limite de cota atingido. Pausa $pausas/$MAX_PAUSAS: dormindo até $(date -r "$wake" '+%F %H:%M') (${espera}s) para retomar os pendentes."
    sleep "$espera"
    log "Reset liberado. Retomando os processos pendentes."
    continue                                # refaz o MESMO processo (índice não avança)
  fi

  i=$(( i + 1 ))
done

log "===== Fim ====="
