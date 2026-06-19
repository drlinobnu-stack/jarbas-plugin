# Jarbas (plugin do Claude Code)

Agente **Jarbas**: pré-laudos e laudos periciais do Dr. Francisco Salvador Brod Lino.
Empacota as 6 skills, os geradores ODT, os templates, as pesquisas por doença e a rotina noturna, para instalar em qualquer máquina.

## O que vem dentro

- **skills/** (6): `jarbas`, `jarbas-pre-laudo` (INSS), `jarbas-interdicao`, `jarbas-medicamentos`, `jarbas-securitaria`, `jarbas-completar` (pós-perícia).
- **scripts/**: geradores Python (`gerar_prelaudo*.py`, `completar_laudo.py`), templates (`template_base.odt`, `template_laudo.doc`), `pesquisas_doencas/`, `anexo3_decreto3048.txt`, `rodar_prelaudos.sh`, `prelaudo_base.conf`.
- **automacao/**: os dois `launchd` (verificação 20h, geração 22h) e o instalador.

## Instalar em uma máquina nova

### 1. Skills (uso interativo: /jarbas...)
No Claude Code da máquina nova:

```
/plugin marketplace add <URL-do-repositorio-git>
/plugin install jarbas@jarbas-lino
```

Isso disponibiliza as skills do Jarbas em qualquer projeto, naquela máquina.

### 2. Execução (geradores + rotina noturna)
As skills sozinhas não bastam para a rotina automática: os scripts Python e o launchd vivem fora do Claude. Rode o instalador uma vez:

```
bash ~/.claude/plugins/.../jarbas/install.sh
```

(ou rode `jarbas/install.sh` direto do repositório clonado). Ele:
- copia os scripts/templates para `~/.claude/scripts/`;
- opcionalmente ativa a rotina noturna (launchd), ajustando os caminhos ao usuário da máquina;
- preserva um `prelaudo_base.conf` já existente.

### 3. Ajustar o caminho dos autos (rede local)
Edite `~/.claude/scripts/prelaudo_base.conf` e aponte para a pasta na rede:

```
PASTA="/Volumes/SEU_SHARE/01PRÉ_LAUDO"
```

O compartilhamento de rede precisa estar **montado** (de preferência de forma persistente) quando a rotina rodar às 22h. Para a automação noturna, use uma máquina dedicada, na tomada, com o share montado de forma estável.

## Atualizar

Como é um plugin git, ao mudar algo neste repositório, em cada máquina:

```
/plugin marketplace update jarbas-lino
```

e rode de novo o `install.sh` se os scripts mudaram.

## O que NÃO viaja no plugin (config por máquina)

- O caminho da pasta dos autos (`prelaudo_base.conf`).
- O `claude` instalado e logado, com cota.
- A montagem do compartilhamento de rede.
- Os MCPs (Gmail, Drive) se forem usados.
