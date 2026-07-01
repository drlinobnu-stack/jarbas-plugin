#!/bin/bash
# Exporta uma cópia de TODAS as skills do JARBAS (e os scripts que elas usam)
# para as pastas pessoais do Claude Code: ~/.claude/skills e ~/.claude/scripts.
#
# Antes de sobrescrever uma skill que JÁ EXISTE no destino, pergunta o que fazer
# (evita substituir versões editadas à mão). Por padrão, NÃO sobrescreve.
#
# Uso:
#   bash exportar_para_claude.sh           # modo interativo (pergunta caso a caso)
#   bash exportar_para_claude.sh --force   # sobrescreve tudo, sem perguntar
#   bash exportar_para_claude.sh --skip    # nunca sobrescreve (pula os já existentes)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/jarbas"
DEST_SK="$HOME/.claude/skills"
DEST_SC="$HOME/.claude/scripts"

MODE="ask"
case "${1:-}" in
  --force) MODE="force" ;;
  --skip)  MODE="skip"  ;;
  "")      MODE="ask"   ;;
  *) echo "Opção inválida: $1 (use --force, --skip ou nada)"; exit 1 ;;
esac

mkdir -p "$DEST_SK" "$DEST_SC"

# ── Backup antes de qualquer sobrescrita ─────────────────────────────────────
STAMP="$(date +%Y%m%d_%H%M%S)"
backup_dir="$HOME/.claude/skills_backup_$STAMP"

decidir() {
  # Decide se sobrescreve a skill "$1" (que já existe no destino).
  # Retorna 0 (sim) ou 1 (não).
  local nome="$1"
  case "$MODE" in
    force) return 0 ;;
    skip)  return 1 ;;
    ask)
      local resp
      read -r -p "    A skill '$nome' já existe em ~/.claude/skills. Sobrescrever? [s/N] " resp </dev/tty
      [[ "${resp:-N}" =~ ^[sS]$ ]] && return 0 || return 1
      ;;
  esac
}

echo "==> Copiando skills para $DEST_SK"
for d in "$SRC"/skills/*/; do
  nome="$(basename "$d")"
  alvo="$DEST_SK/$nome"
  if [ -e "$alvo" ]; then
    if decidir "$nome"; then
      mkdir -p "$backup_dir"
      cp -R "$alvo" "$backup_dir/" 2>/dev/null || true
      rm -rf "$alvo"
      cp -R "$d" "$DEST_SK/"
      echo "    ~ $nome (sobrescrita; backup em $backup_dir)"
    else
      echo "    = $nome (mantida a existente)"
    fi
  else
    cp -R "$d" "$DEST_SK/"
    echo "    + $nome (nova)"
  fi
done

echo "==> Copiando scripts/templates para $DEST_SC"
cp -R "$SRC"/scripts/* "$DEST_SC"/
echo "    (geradores .py, template_base.odt, cabecalho_francisco_lino.png, etc.)"

echo
echo "Pronto. Skills em $DEST_SK e scripts em $DEST_SC."
[ -d "$backup_dir" ] && echo "Backup das skills sobrescritas: $backup_dir"
echo "Recarregue o Claude Code para que as skills pessoais sejam reconhecidas."
