#!/usr/bin/env python3
"""
gerar_conclusao_odt.py  v1.0
Insere a Discussão/Conclusão e as respostas aos quesitos DIRETAMENTE no laudo ODT,
manipulando o content.xml e re-zipando cru (mimetype primeiro). NUNCA reconverte o
ODT pelo LibreOffice, para preservar o cabeçalho (logo) e toda a formatação validada
do JARBAS. Espelha as regras da skill /conclusao1 (estilo do Dr. Lino).

Faz:
  - Insere os blocos da conclusão entre "Discussão / Conclusão:" e "Quesitos:",
    com 1 linha em branco entre blocos e 2 antes de "Dados de interesse pericial:".
  - Preenche cada parágrafo "Resposta:" (na ordem) com a resposta em itálico.
  - Aplica em texto NOVO: remove travessões, "Não se aplica" -> "Prejudicado",
    "dia"/"Dia" antes de datas dd.mm.aaaa.
  - Corrige a data da página 1 para a data de hoje (se diferente).
  - Substitui "xxx (xxx)" das Considerações finais pela contagem real de folhas.

Uso:
  python3 gerar_conclusao_odt.py \
    --laudo  ENTRADA.odt \
    --conclusao  conclusao-texto.txt \
    --respostas  quesitos-respostas.json \
    --saida  SAIDA.odt \
    [--autos NUMERO] [--data-hoje "DD de mês de AAAA"]

quesitos-respostas.json:
  {"quesitos_juizo":[{"numero":"1","resposta":"..."}],
   "quesitos_autor":[...], "quesitos_reu":[...]}
A ordem juízo -> autor -> réu deve bater com a ordem dos "Resposta:" no laudo.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

MESES_PT = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio",
            6: "junho", 7: "julho", 8: "agosto", 9: "setembro", 10: "outubro",
            11: "novembro", 12: "dezembro"}

PARA_RE = re.compile(r'<text:p\b[^>]*/>|<text:p\b[^>]*>.*?</text:p>', re.DOTALL)
PADRAO_DATA = re.compile(
    r'([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .]+),\s*(\d{1,2})\s+de\s+([a-zA-Zà-ÿ]+)\s+de\s+(\d{4})')
PADRAO_XXX = re.compile(r'xxx\s*\(\s*xxx\s*\)', re.IGNORECASE)
ESTILO_ITALICO = ('<style:style style:name="CONC_IT" style:family="text">'
                  '<style:text-properties style:font-name="Arial" '
                  'fo:font-style="italic" style:font-style-asian="italic" '
                  'fo:font-size="12pt"/></style:style>')


def x(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def plain(frag):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', frag)).strip()


def pstyle(frag):
    m = re.search(r'text:style-name="([^"]+)"', frag)
    return m.group(1) if m else None


def data_hoje_extenso():
    h = date.today()
    return f"{h.day} de {MESES_PT[h.month]} de {h.year}"


def numero_por_extenso(n):
    u = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito',
         'nove', 'dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis',
         'dezessete', 'dezoito', 'dezenove']
    d = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta',
         'oitenta', 'noventa']
    c = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos',
         'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    if n == 0:
        return 'zero'
    if n == 100:
        return 'cem'
    if n < 20:
        return u[n]
    if n < 100:
        a, b = divmod(n, 10)
        return d[a] + (' e ' + u[b] if b else '')
    a, r = divmod(n, 100)
    return c[a] + (' e ' + numero_por_extenso(r) if r else '')


# ── transformações do texto NOVO ──────────────────────────────────────────────

def remover_travessoes(texto):
    for t in ['—', '–']:
        texto = re.sub(r'\s*' + re.escape(t) + r'\s*', ', ', texto)
    texto = re.sub(r'(?<=\w)\s+-\s+(?=\w)', ', ', texto)
    return texto


def nao_se_aplica(texto):
    return re.sub(r'[Nn]ão\s+se\s+aplica\.?', 'Prejudicado.', texto)


def dia_antes_datas(texto):
    out, fim = [], 0
    for m in re.finditer(r'\b(\d{2}\.\d{2}\.\d{4})\b', texto):
        antes = texto[fim:m.start()]
        st = antes.rstrip()
        if re.search(r'\bdia\s*$', st, re.IGNORECASE):
            out.append(antes + m.group(0))
        elif not st or st[-1] in '.!?:':
            out.append(antes + 'Dia ' + m.group(0))
        else:
            out.append(antes + 'dia ' + m.group(0))
        fim = m.end()
    out.append(texto[fim:])
    return ''.join(out)


def proc_texto(texto):
    return dia_antes_datas(remover_travessoes(nao_se_aplica(texto)))


# ── inserção da conclusão ─────────────────────────────────────────────────────

def achar_paragrafos(content):
    return list(PARA_RE.finditer(content))


def e_titulo_conclusao(p):
    return bool(re.match(r'^\d*\.?\s*Discuss[aã]o\s*/\s*Conclus[aã]o\s*:?\s*$',
                         plain(p), re.IGNORECASE))


def e_titulo_quesitos(p):
    return bool(re.match(r'^\d*\.?\s*Quesitos\s*:?\s*$', plain(p), re.IGNORECASE))


def estilo_corpo(content):
    """Estilo de corpo do laudo = o estilo da ANAMNESE (parágrafo "Refere ..."
    da seção 3, Histórico da doença). Assim a conclusão fica idêntica ao corpo,
    seja qual for a arquitetura de estilos do template (varia por laudo)."""
    for anc in (r'Refere\s+a\s+autora', r'Refere\s+o\s+autor',
                r'Refere\s+que', r'Refere[- ]se'):
        m = re.search(r'<text:p text:style-name="([^"]+)"[^>]*>\s*'
                      r'(?:<text:soft-page-break/>)?\s*' + anc, content)
        if m:
            return m.group(1)
    # fallback: 1º parágrafo longo após "Histórico da doença"
    h = content.find("Histórico da doença")
    if h != -1:
        for m in PARA_RE.finditer(content[h:]):
            if len(plain(m.group(0))) >= 60:
                s = pstyle(m.group(0))
                if s:
                    return s
    return estilo_corpo_dominante(content)


def estilo_corpo_dominante(content):
    """Estilo de corpo do laudo (Arial 12, justificado, PRETO). Entre as frases
    longas fora de tabelas, prefere o estilo cuja própria definição força a cor
    preta (fo:color="#000000") — é o estilo de corpo do Dr. (ex.: anamnese). Evita
    estilos que herdam o cinza do "Standard". Cai no mais frequente se não achar."""
    defs = {m.group(1): m.group(0) for m in re.finditer(
        r'<style:style[^>]*style:name="([^"]+)"[^>]*>.*?</style:style>',
        content, re.DOTALL)}
    sem_tabelas = re.sub(r'<table:table\b.*?</table:table>', '', content, flags=re.DOTALL)
    todos, pretos = {}, {}
    for m in PARA_RE.finditer(sem_tabelas):
        frag = m.group(0)
        if len(plain(frag)) < 40:
            continue
        s = pstyle(frag)
        if not s:
            continue
        todos[s] = todos.get(s, 0) + 1
        if 'fo:color="#000000"' in defs.get(s, ''):
            pretos[s] = pretos.get(s, 0) + 1
    if pretos:
        return max(pretos, key=pretos.get)
    return max(todos, key=todos.get) if todos else None


def inserir_conclusao(content, blocos):
    paras = achar_paragrafos(content)
    i_tit = next((k for k, m in enumerate(paras)
                  if e_titulo_conclusao(m.group(0))), None)
    if i_tit is None:
        return content, 0, "titulo 'Discussão / Conclusão:' não localizado"
    i_que = next((k for k in range(i_tit + 1, len(paras))
                  if e_titulo_quesitos(paras[k].group(0))), None)

    ini = paras[i_tit].end()
    if i_que is not None:
        fim = paras[i_que].start()
        regiao = [paras[k] for k in range(i_tit + 1, i_que)]
    else:
        fim = paras[i_tit].end()
        regiao = []

    # estilo de corpo = o estilo de corpo PRETO do laudo (igual à anamnese), para a
    # conclusão sair com a mesma letra/cor/tamanho do corpo (não o cinza herdado do
    # "Standard"). Decisão do Dr. (29/06/2026): a conclusão acompanha o corpo.
    estilo = estilo_corpo(content) or 'Standard'

    # único destaque: "Dados de interesse pericial:" em negrito. O caput do Art. 86
    # fica no MESMO estilo do corpo (o Dr. removeu o negrito/recuo/11pt em 29/06/2026).
    estilos_extra = (
        '<style:style style:name="CONC_BD" style:family="text">'
        '<style:text-properties fo:font-weight="bold" style:font-weight-asian="bold"/></style:style>')

    def paragrafo(b):
        if b.lower().startswith('dados de interesse'):
            return (f'<text:p text:style-name="{estilo}">'
                    f'<text:span text:style-name="CONC_BD">{x(b)}</text:span></text:p>')
        return f'<text:p text:style-name="{estilo}">{x(b)}</text:p>'

    blocos = [b.strip() for b in blocos if b.strip()]
    # 1 linha em branco logo após o título "Discussão / Conclusão:"
    partes = [f'<text:p text:style-name="{estilo}"/>']
    for j, b in enumerate(blocos):
        if j > 0:
            nb = 2 if blocos[j].lower().startswith('dados de interesse') else 1
            partes += [f'<text:p text:style-name="{estilo}"/>'] * nb
        partes.append(paragrafo(b))
    novo = ''.join(partes)

    content = content[:ini] + novo + content[fim:]
    if 'style:name="CONC_BD"' not in content:
        content = content.replace('<office:automatic-styles>',
                                  '<office:automatic-styles>' + estilos_extra, 1)
    return content, len(blocos), f"{len(blocos)} blocos inseridos (estilo {estilo})"


# ── preenchimento das respostas ───────────────────────────────────────────────

def inserir_respostas(content, dados):
    respostas = []
    for chave in ('quesitos_juizo', 'quesitos_autor', 'quesitos_reu'):
        for q in dados.get(chave, []):
            respostas.append((q.get('resposta') or '').strip())

    it = iter(respostas)
    estado = {'preench': 0, 'branco': 0, 'sobra': 0}

    def repl(m):
        frag = m.group(0)
        if frag.endswith('/>'):          # parágrafo vazio self-closing
            return frag
        # texto puro do parágrafo (sem tags), para detectar um "Resposta:" ainda
        # vazio, esteja ele em texto direto, dentro de <text:span> ou após um
        # <text:soft-page-break/>. Robusto a variações do template.
        puro = html.unescape(re.sub(r'<[^>]+>', '', frag))
        if re.sub(r'\s+', ' ', puro).strip().lower() != 'resposta:':
            return frag
        try:
            r = next(it)
        except StopIteration:
            estado['sobra'] += 1
            return frag
        if not r:
            estado['branco'] += 1
            return frag
        estado['preench'] += 1
        r = proc_texto(r)
        corpo, _, _ = frag.rpartition('</text:p>')
        return (corpo + ' <text:span text:style-name="CONC_IT">'
                + x(r) + '</text:span></text:p>')

    content = PARA_RE.sub(repl, content)
    return content, estado


# ── correções ─────────────────────────────────────────────────────────────────

def garantir_estilo_italico(content):
    if 'style:name="CONC_IT"' in content:
        return content
    return content.replace('<office:automatic-styles>',
                           '<office:automatic-styles>' + ESTILO_ITALICO, 1)


def _valor_celula(content, rotulo):
    """Valor da célula seguinte ao rótulo (ex.: 'Peso (kg)') na tabela do exame."""
    m = re.search(re.escape(rotulo) + r'[^<]*</text:p></table:table-cell>\s*'
                  r'<table:table-cell\b[^>]*>\s*<text:p\b[^>]*>([\d.,]+)</text:p>',
                  content, re.DOTALL)
    return m.group(1) if m else None


def completar_imc(content):
    """Calcula o IMC pelo peso/altura do exame, preenche o valor na célula do IMC
    e deixa SOMENTE a faixa correspondente (apaga as demais faixas). Regra do Dr."""
    p = _valor_celula(content, 'Peso (kg)')
    a = _valor_celula(content, 'Altura (m)')
    if not p or not a:
        return content, "IMC: peso/altura não localizados"
    peso = float(p.replace(',', '.'))
    alt = float(a.replace(',', '.'))
    if alt > 3:                      # veio em cm
        alt /= 100
    if alt <= 0:
        return content, "IMC: altura inválida"
    imc = peso / (alt * alt)
    imc_str = f"{imc:.2f}".replace('.', ',')
    idx = (0 if imc < 18.5 else 1 if imc < 25 else 2 if imc < 30
           else 3 if imc < 35 else 4 if imc < 40 else 5)

    logs = []
    # 1) preencher o valor na célula vazia ao lado de "IMC:"
    def fill(m):
        return m.group(1) + '>' + imc_str + '</text:p>'
    content, n = re.subn(
        r'(IMC:\s*</text:p></table:table-cell>\s*<table:table-cell\b[^>]*>\s*'
        r'<text:p\b[^>]*?)\s*/>', fill, content, count=1)
    logs.append(f"valor {imc_str}" if n else "valor (célula não localizada)")

    # 2) manter só a faixa correspondente no parágrafo das 6 faixas (extração por
    # índice para não pegar o parágrafo vazio anterior)
    pos = content.find("Abaixo do peso")
    if pos != -1:
        op_start = content.rfind("<text:p", 0, pos)
        op_end = content.find(">", op_start) + 1
        open_tag = content[op_start:op_end]
        obes = content.find("Obesidade", pos)
        fim = content.find("</text:p>", obes if obes != -1 else pos)
        if op_start != -1 and fim != -1 and not open_tag.endswith("/>"):
            inner = content[op_end:fim]
            puro = re.sub(r'<[^>]+>', '', inner)
            # extrai a faixa pelo padrão (robusto: serve com ou sem quebras de linha)
            pats = [
                r'18,5\s*[–-]\s*Abaixo do peso',
                r'18,5\s*[–-]\s*24,9\s*[–-]\s*Normal',
                r'25,0\s*[–-]\s*29,9\s*[–-]\s*Excesso de peso',
                r'30,0\s*[–-]\s*34,9\s*[–-]\s*Obesidade Leve \(Grau I\)',
                r'35,0\s*[–-]\s*39,9\s*[–-]\s*Obesidade Severa \(Grau II\)',
                r'40,0\s*[–-]\s*Obesidade M[óo]rbida \(Grau III\)',
            ]
            mm = re.search(pats[idx], puro)
            faixa = mm.group(0).strip() if mm else puro.strip()
            novo = open_tag + x(faixa) + "</text:p>"
            content = content[:op_start] + novo + content[fim + len("</text:p>"):]
            logs.append(f"faixa: {faixa}")
        else:
            logs.append("parágrafo de faixas não delimitado")
    else:
        logs.append("parágrafo de faixas não localizado")
    return content, "IMC: " + "; ".join(logs)


def corrigir_data_p1(content, data_hoje):
    # primeira data "Cidade, DD de mês de AAAA" do corpo (linha da assinatura, p.1)
    pos = content.find('<office:body>')
    base = content[pos:] if pos != -1 else content
    m = PADRAO_DATA.search(base)
    if not m:
        return content, "data da página 1 não localizada"
    cidade = m.group(1).strip()
    original = m.group(0)
    nova = f"{cidade}, {data_hoje}"
    if original == nova:
        return content, f"data confirmada: {original}"
    return content.replace(original, nova, 1), f"data corrigida: '{original}' -> '{nova}'"


SOFFICE_CANDS = (
    'soffice', 'libreoffice',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    '/usr/local/bin/soffice', '/opt/homebrew/bin/soffice',
)


def _soffice_bin():
    import shutil
    for c in SOFFICE_CANDS:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        if shutil.which(c):
            return c
    return None


def _paginas_do_pdf(pdf_bytes):
    """Conta páginas lendo o PDF, sem depender do poppler/pdfinfo.
    Primário: maior /Count de um nó /Type /Pages (a raiz tem o total).
    Fallback: número de objetos /Type /Page (quando não há object streams)."""
    contagens = []
    for m in re.finditer(rb'/Type\s*/Pages\b', pdf_bytes):
        c = re.search(rb'/Count\s+(\d+)', pdf_bytes[m.start():m.start() + 300])
        if c:
            contagens.append(int(c.group(1)))
    if contagens:
        return max(contagens)
    if b'/ObjStm' not in pdf_bytes:
        n = len(re.findall(rb'/Type\s*/Page[^s]', pdf_bytes))
        if n:
            return n
    return 0


def contar_paginas_odt(odt_path):
    binario = _soffice_bin()
    if not binario:
        return 0
    try:
        with tempfile.TemporaryDirectory() as td:
            perfil = Path(td) / 'lo_profile'
            subprocess.run([binario, '--headless',
                            f'-env:UserInstallation=file://{perfil}',
                            '--convert-to', 'pdf', odt_path, '--outdir', td],
                           capture_output=True, timeout=120)
            pdf = Path(td) / (Path(odt_path).stem + '.pdf')
            if not pdf.exists():
                return 0
            return _paginas_do_pdf(pdf.read_bytes())
    except Exception:
        pass
    return 0


def patch_paginas(odt_path):
    n = contar_paginas_odt(odt_path)
    if n <= 0:
        return "contagem de páginas indisponível (xxx mantido)"
    sub = f"{n} ({numero_por_extenso(n)})"
    with zipfile.ZipFile(odt_path) as z:
        base = {i.filename: z.read(i.filename) for i in z.infolist()}
    content = base['content.xml'].decode('utf-8')
    novo, k = PADRAO_XXX.subn(sub, content)
    if k == 0:
        return f"'xxx (xxx)' não encontrado (páginas={n})"
    base['content.xml'] = novo.encode('utf-8')
    _escrever_odt(odt_path, base)
    return f"folhas: {sub}"


def _escrever_odt(saida, base):
    with zipfile.ZipFile(saida, 'w', zipfile.ZIP_DEFLATED) as z:
        if 'mimetype' in base:
            z.writestr(zipfile.ZipInfo('mimetype'), base['mimetype'],
                       compress_type=zipfile.ZIP_STORED)
        for name, data in base.items():
            if name != 'mimetype':
                z.writestr(name, data)


def gerar(laudo, conclusao, respostas, saida, data_hoje=None, autos=""):
    data_hoje = data_hoje or data_hoje_extenso()
    with zipfile.ZipFile(laudo) as z:
        base = {i.filename: z.read(i.filename) for i in z.infolist()}
    content = base['content.xml'].decode('utf-8')
    logs = []

    content = garantir_estilo_italico(content)

    if conclusao and Path(conclusao).exists():
        texto = remover_travessoes(open(conclusao, encoding='utf-8').read())
        blocos = texto.split('\n\n') if '\n\n' in texto else texto.split('\n')
        content, _, msg = inserir_conclusao(content, blocos)
        logs.append("  Conclusão: " + msg)
    else:
        logs.append("  Conclusão: arquivo não fornecido")

    if respostas and Path(respostas).exists():
        dados = json.load(open(respostas, encoding='utf-8'))
        content, est = inserir_respostas(content, dados)
        logs.append(f"  Quesitos: {est['preench']} preenchidos, "
                    f"{est['branco']} em branco, {est['sobra']} respostas sem campo")
    else:
        logs.append("  Quesitos: JSON não fornecido")

    content, msg = corrigir_data_p1(content, data_hoje)
    logs.append("  " + msg)

    content, msg = completar_imc(content)
    logs.append("  " + msg)

    # validar XML
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        ln, col = e.position
        ctx = content.split('\n')[ln - 1][max(0, col - 80):col + 120]
        print(f"ERRO XML linha {ln}: {e}\n  Contexto: {ctx[:200]}")
        sys.exit(1)

    base['content.xml'] = content.encode('utf-8')
    _escrever_odt(saida, base)

    logs.append("  " + patch_paginas(saida))

    print(f"\nConcluído: {saida}")
    for l in logs:
        print(l)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Insere conclusão e respostas no laudo ODT")
    ap.add_argument("--laudo", required=True)
    ap.add_argument("--conclusao", default="")
    ap.add_argument("--respostas", default="")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--data-hoje", default=None)
    ap.add_argument("--autos", default="")
    a = ap.parse_args()
    if not Path(a.laudo).exists():
        print(f"Laudo não encontrado: {a.laudo}")
        sys.exit(1)
    gerar(a.laudo, a.conclusao, a.respostas, a.saida, a.data_hoje, a.autos)
