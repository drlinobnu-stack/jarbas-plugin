#!/bin/bash
# Instalador do plugin JARBAS em uma máquina nova (macOS).
# Coloca os scripts/templates em ~/.claude/scripts e (opcional) ativa a rotina noturna.
# As SKILLS já vêm pelo plugin do Claude Code; este script cuida da parte de execução
# (scripts Python + automação launchd), que vive fora do Claude.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/scripts"
mkdir -p "$DEST"

echo "==> Instalando scripts e templates em $DEST"
# Copia tudo, mas NÃO sobrescreve o prelaudo_base.conf se já existir (preserva o caminho local).
for f in "$PLUGIN_DIR"/scripts/*; do
  base="$(basename "$f")"
  if [ "$base" = "prelaudo_base.conf" ] && [ -f "$DEST/$base" ]; then
    echo "    mantendo $base existente (não sobrescrito)"
    continue
  fi
  cp -R "$f" "$DEST/"
done
chmod +x "$DEST"/*.sh 2>/dev/null || true

# Detecta o binário do claude para a automação
CLAUDE_BIN="$(command -v claude || echo /usr/local/bin/claude)"
echo "==> claude detectado em: $CLAUDE_BIN"

read -r -p "Ativar a rotina noturna de pré-laudos (launchd)? [s/N] " RESP
if [[ "${RESP:-N}" =~ ^[sS]$ ]]; then
  LA="$HOME/Library/LaunchAgents"
  mkdir -p "$LA"
  for plist in "$PLUGIN_DIR"/automacao/*.plist; do
    name="$(basename "$plist")"
    # Ajusta o caminho do usuário (/Users/franciscolino -> seu HOME) ao instalar.
    sed "s#/Users/franciscolino#$HOME#g" "$plist" > "$LA/$name"
    launchctl unload "$LA/$name" 2>/dev/null || true
    launchctl load "$LA/$name"
    echo "    carregado: $name"
  done
  echo "    rotina ativada (verificação 20h, geração 22h)."
else
  echo "    rotina noturna NÃO ativada (você pode rodar depois)."
fi

echo
echo "==> FALTA AJUSTAR O CAMINHO DOS AUTOS (pasta na rede local):"
echo "    edite  $DEST/prelaudo_base.conf  e defina a linha:"
echo "      PASTA=\"/Volumes/SEU_SHARE/01PRÉ_LAUDO\""
echo "    (o compartilhamento precisa estar montado, de preferência de forma persistente)."
echo
echo "Pronto. As skills do Jarbas já estão disponíveis via plugin (/jarbas...)."
