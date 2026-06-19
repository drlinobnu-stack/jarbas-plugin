#!/usr/bin/env python3
"""
Completa um laudo ODT já pronto com exames/atestados que o autor trouxe na perícia.
CIENTE DE ESTILO: localiza as tabelas pelo CABEÇALHO (não pelo nome/numeração) e
clona os estilos do PRÓPRIO documento, funcionando tanto nos laudos Word do Dr.
quanto nos ODT gerados pelo JARBAS. No caso de exames, se houver uma linha-modelo
em branco + "CONCLUSÃO:" (padrão do modelo Word), ela é preenchida no lugar.

Uso: python3 completar_laudo.py laudo_entrada.odt dados_novos.json laudo_saida.odt

dados_novos.json:
{
  "exames":    [{"data":"24/08/24","exame":"TC do Crânio","folha":"Apresentado na perícia","conclusao":"linha1\\nlinha2"}],
  "atestados": [{"data":"20/07/24","motivo":"Resumo de alta","medico":"-","folha":"Apresentado na perícia"}]
}
"""
import sys, json, os, zipfile, re

FOLHA_PADRAO = "Apresentado na perícia"


def x(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


# ── utilidades de parsing ─────────────────────────────────────────────────────

def _rows(block):
    return re.findall(r'<table:table-row\b.*?</table:table-row>', block, re.DOTALL)

def _cells(row):
    return re.findall(r'<table:table-cell\b.*?</table:table-cell>', row, re.DOTALL)

def _row_open(row):
    return re.match(r'<table:table-row\b[^>]*>', row).group(0)

def _cell_open(cell):
    return re.match(r'<table:table-cell\b[^>]*>', cell).group(0)

def _paras(cell):
    return re.findall(r'<text:p\b[^>]*/>|<text:p\b.*?</text:p>', cell, re.DOTALL)

def _pstyle(frag):
    m = re.search(r'text:style-name="([^"]+)"', frag)
    return m.group(1) if m else None

def _plain(frag):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', frag)).strip()

def _make_cell(cell_tpl, texto):
    """Recria uma célula com os mesmos estilos do modelo, trocando só o texto."""
    op = _cell_open(cell_tpl)
    ps = _pstyle((_paras(cell_tpl) or [''])[0])
    par = (f'<text:p text:style-name="{ps}">{x(texto)}</text:p>' if ps
           else f'<text:p>{x(texto)}</text:p>')
    return op + par + '</table:table-cell>'

def _split_block(block):
    """Devolve (prefixo_ate_primeira_row, lista_de_rows, sufixo)."""
    i = block.index('<table:table-row')
    j = block.rindex('</table:table-row>') + len('</table:table-row>')
    return block[:i], _rows(block[i:j]), block[j:]


# ── localizar tabelas pelo cabeçalho ──────────────────────────────────────────

def _find_table(content, want_all, want_none=()):
    for m in re.finditer(r'<table:table\b.*?</table:table>', content, re.DOTALL):
        head = _plain(m.group(0)[:1200]).upper()
        if all(w.upper() in head for w in want_all) and not any(w.upper() in head for w in want_none):
            return m.start(), m.end(), m.group(0)
    return None


# ── ATESTADOS: clonar última linha de dados e acrescentar ─────────────────────

def _is_header_or_title(row):
    t = _plain(row).upper()
    return ('MOTIVO' in t and 'MÉDICO' in t) or 'ATESTADOS E DECLARAÇÕES' in t or \
           (t.replace('DATA', '').replace('EXAME', '').replace('Nº FOLHA', '').strip() == '')

def _completar_atestados(content, novos):
    loc = _find_table(content, ['MOTIVO', 'MÉDICO'])
    if not loc:
        return content, None
    s, e, block = loc
    prefix, rows, suffix = _split_block(block)
    # modelo = última linha com 4 células que não é título/cabeçalho
    tpl = None
    for r in rows:
        if len(_cells(r)) >= 4 and not _is_header_or_title(r):
            tpl = r
    if tpl is None:
        # fallback: usa a linha de cabeçalho como molde de estrutura
        for r in rows:
            if len(_cells(r)) >= 4:
                tpl = r
    cells = _cells(tpl)
    existente = _plain(block)
    novas = ''
    n = 0
    for a in novos:
        motivo = a.get('motivo', '')
        data = a.get('data', '')
        # já presente (evita duplicar em re-execução): só pula se o mesmo motivo
        # já consta E (sem data informada OU a mesma data também consta). Assim um
        # documento de mesmo nome em data diferente NÃO é barrado.
        if motivo and motivo in existente and (not data or data in existente):
            continue
        vals = [a.get('data', '*'), motivo, a.get('medico', '-'), a.get('folha', FOLHA_PADRAO)]
        novas += _row_open(tpl) + ''.join(_make_cell(cells[i], vals[i]) for i in range(4)) + '</table:table-row>'
        n += 1
    novo_block = prefix + ''.join(rows) + novas + suffix
    return content[:s] + novo_block + content[e:], n


# ── EXAMES: preencher linha-modelo em branco ou clonar par (dados + CONCLUSÃO) ─

def _row_vazia_dados(row):
    cells = _cells(row)
    if len(cells) != 3:
        return False
    return all(_plain(c) == '' for c in cells)

def _is_conclusao(row):
    # tolera o rótulo quebrado em spans (ex.: "CONCL"+"USÃO" -> "CONCL USÃO")
    return 'CONCLUS' in _plain(row).upper().replace(' ', '')

def _is_header_exame(row):
    t = _plain(row).upper()
    return 'EXAME' in t and 'FOLHA' in t and 'MOTIVO' not in t

def _build_par_conclusao(concl_tpl, conclusao):
    """Mantém o rótulo CONCLUSÃO do modelo e troca as linhas de conteúdo."""
    spanned = _cells(concl_tpl)[0]
    op_cell = _cell_open(spanned)
    paras = _paras(spanned)
    label = paras[0] if paras else '<text:p>CONCLUSÃO:</text:p>'
    estilo = _pstyle(paras[1]) if len(paras) > 1 else _pstyle(label)
    linhas = [l for l in (conclusao or '').split('\n') if l.strip()] or ['']
    corpo = ''.join(
        (f'<text:p text:style-name="{estilo}">{x(l)}</text:p>' if estilo else f'<text:p>{x(l)}</text:p>')
        for l in linhas)
    novo_cell = op_cell + label + corpo + '</table:table-cell>'
    covered = ''.join(re.findall(r'<table:covered-table-cell/>', concl_tpl))
    return _row_open(concl_tpl) + novo_cell + covered + '</table:table-row>'

def _build_row_dados(dados_tpl, data, exame, folha):
    cells = _cells(dados_tpl)
    vals = [data, exame, folha]
    return _row_open(dados_tpl) + ''.join(_make_cell(cells[i], vals[i]) for i in range(3)) + '</table:table-row>'

def _completar_exames(content, novos):
    loc = _find_table(content, ['EXAME', 'FOLHA'], want_none=['MOTIVO', 'Peso (kg)'])
    if not loc:
        return content, None
    s, e, block = loc
    prefix, rows, suffix = _split_block(block)

    # modelos de linha
    dados_tpl = None
    concl_tpl = None
    for i, r in enumerate(rows):
        if _is_conclusao(r):
            concl_tpl = concl_tpl or r
        elif len(_cells(r)) == 3 and not _is_header_exame(r):
            dados_tpl = dados_tpl or r
    # par-modelo em branco (linha de dados vazia seguida de CONCLUSÃO vazia)
    idx_placeholder = None
    for i, r in enumerate(rows):
        if _row_vazia_dados(r):
            idx_placeholder = i
            break

    existente = _plain(block)
    novas = ''
    n = 0
    for ex in novos:
        exame = ex.get('exame', '')
        data = ex.get('data', '')
        # já presente (evita duplicar em re-execução): só pula se o mesmo exame
        # já consta E (sem data informada OU a mesma data também consta). Assim um
        # exame de mesmo nome em data diferente (ex.: RM repetida anos depois) NÃO é barrado.
        if exame and exame in existente and (not data or data in existente):
            continue
        novas += _build_row_dados(dados_tpl, ex.get('data', ''), exame,
                                  ex.get('folha', FOLHA_PADRAO))
        if concl_tpl is not None:
            novas += _build_par_conclusao(concl_tpl, ex.get('conclusao', ''))
        n += 1

    if idx_placeholder is not None and n > 0:
        # remove a linha de dados em branco e a CONCLUSÃO vazia que a segue
        rem = {idx_placeholder}
        if idx_placeholder + 1 < len(rows) and _is_conclusao(rows[idx_placeholder + 1]):
            rem.add(idx_placeholder + 1)
        rows = [r for k, r in enumerate(rows) if k not in rem]

    novo_block = prefix + ''.join(rows) + novas + suffix
    return content[:s] + novo_block + content[e:], n


# ── PRINCIPAL ─────────────────────────────────────────────────────────────────

def completar(laudo_in, dados, laudo_out):
    with zipfile.ZipFile(laudo_in) as z:
        base = {n: z.read(n) for n in z.namelist()}
    content = base['content.xml'].decode('utf-8')
    resumo = []

    def msg(n, tabela, palavra):
        if n is None:
            return f"AVISO: tabela de {tabela} não localizada no laudo"
        if n == 0:
            return f"{tabela}: nada a inserir (documento(s) já presente(s))"
        return f"{n} {palavra} acrescentado(s) em {tabela}"

    novos_atest = dados.get('atestados', [])
    if novos_atest:
        content, n = _completar_atestados(content, novos_atest)
        resumo.append(msg(n, "Atestados/Declarações", "documento(s)"))

    novos_exames = dados.get('exames', [])
    if novos_exames:
        content, n = _completar_exames(content, novos_exames)
        resumo.append(msg(n, "Exames complementares", "exame(s)"))

    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(content)
    except ET.ParseError as ex:
        line, col_n = ex.position
        ctx = content.split('\n')[line - 1][max(0, col_n - 80):col_n + 160]
        print(f"ERRO XML linha {line}: {ex}\n  Contexto: {ctx[:200]}")
        sys.exit(1)

    base['content.xml'] = content.encode('utf-8')
    with zipfile.ZipFile(laudo_out, 'w', zipfile.ZIP_DEFLATED) as zout:
        if 'mimetype' in base:
            zout.writestr(zipfile.ZipInfo('mimetype'), base['mimetype'])
        for name, data in base.items():
            if name != 'mimetype':
                zout.writestr(name, data)

    print(f"Laudo completado: {laudo_out}")
    for r in resumo:
        print("  - " + r)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 completar_laudo.py laudo_entrada.odt dados_novos.json laudo_saida.odt")
        sys.exit(1)
    with open(sys.argv[2], encoding='utf-8') as f:
        dados = json.load(f)
    completar(sys.argv[1], dados, sys.argv[3])
