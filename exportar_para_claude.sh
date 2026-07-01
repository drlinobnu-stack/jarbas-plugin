#!/bin/bash
# Exporta uma cópia de TODAS as skills do JARBAS (e os scripts que elas usam)
# para as pastas pessoais do Claude Code: ~/.claude/skills e ~/.claude/scripts.
#
# Uso:  bash exportar_para_claude.sh
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/jarbas"
DEST_SK="$HOME/.claude/skills"
DEST_SC="$HOME/.claude/scripts"

mkdir -p "$DEST_SK" "$DEST_SC"

echo "==> Copiando skills para $DEST_SK"
for d in "$SRC"/skills/*/; do
  nome="$(basename "$d")"
  cp -R "$d" "$DEST_SK/"
  echo "    + $nome"
done

echo "==> Copiando scripts/templates para $DEST_SC"
cp -R "$SRC"/scripts/* "$DEST_SC"/
echo "    (geradores .py, template_base.odt, cabecalho_francisco_lino.png, etc.)"

echo
echo "Pronto. Skills exportadas para $DEST_SK e scripts para $DEST_SC."
echo "Recarregue o Claude Code para que as skills pessoais sejam reconhecidas."
