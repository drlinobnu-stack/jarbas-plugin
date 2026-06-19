#!/usr/bin/env python3
"""
Gerador de Pré-Laudo Pericial de INTERDIÇÃO / CURATELA — ODT
Reaproveita EXATAMENTE a formatação do pré-laudo previdenciário (mesmo template_base.odt,
mesmos estilos, fontes, tamanhos, títulos e espaçamentos). Muda apenas a ESTRUTURA:
- "Interditando" no lugar de "Réu"; aceita várias partes autoras e vários interditandos
- Finalidade: "Avaliação de interdição e curatela."
- Remove Benefícios, CAT, CNIS e Antecedentes (não se aplicam à interdição)
- Exame físico vira exame do estado mental (campos em branco, preenchidos na perícia)
- Quesitos do juízo: conjunto fixo a–g (padrão das interdições)
- Numeração própria das seções

Uso: python3 gerar_prelaudo_interdicao.py dados.json saida.odt
"""
import sys, json, os, zipfile, re

# Reusa todo o maquinário de estilo/tabelas do gerador previdenciário
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_prelaudo as G
x = G.x

# ── Quesitos do juízo: conjunto FIXO das interdições (a–g) ─────────────────────
QUESITOS_JUIZO_PADRAO = [
    {"letra": "a", "enunciado": "O(a) interditando é portador de alguma deficiência mental ou outra enfermidade física? Qual?"},
    {"letra": "b", "enunciado": "Em caso positivo, tal doença impede o necessário discernimento para os atos da vida civil? O(a) interditando(a) consegue exprimir sua vontade?"},
    {"letra": "c", "enunciado": "Em caso de ser o(a) interditando(a) possuidor(a) de enfermidade incapacitante, qual o alcance das limitações de compreensão do(a) mesmo(a)?"},
    {"letra": "d", "enunciado": "Eventual enfermidade constatada tem caráter permanente ou temporário, e desde quando o acomete?"},
    {"letra": "e", "enunciado": "O(a) interditando(a) necessita de tratamento continuado? Qual ou quais?"},
    {"letra": "f", "enunciado": "O(a) interditando(a) necessita do auxílio de seus familiares para condução de seus atos e/ou negócios da vida civil, e em que medida? Neste particular, o mero auxílio (tomada de decisões auxiliada) é suficiente ou há a necessidade de ter alguém que pratique esses atos em seu nome?"},
    {"letra": "g", "enunciado": "Outras informações que o(a) expert considerar relevantes."},
]

METODOLOGIA = [
    "1.1 Realização de uma entrevista e exame clínico com o interditando e o informante, definindo sua doença, tratamentos, antecedentes pessoais, hábitos de vida e histórico da doença alegada, sendo facultada a presença dos assistentes técnicos (médicos) das partes, eventualmente nomeados nos autos.",
    "1.2 Avaliação das limitações cognitivas do periciado.",
    "1.3 Definição da capacidade civil do interditando de acordo com os dados obtidos na entrevista e exame clínico.",
]

# Bibliografia FIXA da interdição (psiquiatria forense / medicina legal).
# Cada item: (autor, título-em-itálico, restante). Formatação idêntica ao template (P5 + T8 itálico).
BIBLIOGRAFIA = [
    ("ALCÂNTARA, Hermes Rodrigues de.", "Perícia Médica Judicial", ", Rio de Janeiro: Guanabara Koogan, 2006, 508 p."),
    ("ALTAVILLA, Enrico.", "Psicologia Judiciária", " 3ª ed. Coimbra, Armênio Amado Editor, v II, 1982."),
    ("BASTOS, Cláudio Lyra.", "Manual do exame psíquico - uma introdução prática à psicopatologia", ". 2. ed. Ed. Revinter, 2002."),
    ("BRANDIMILLER, Primo.", "Perícia Judicial em acidentes e doenças do trabalho", ", São Paulo: Editora Senac, 2006, 312 p."),
    ("EPIPHANIO, Emílio Bicalho; VILELA José Ricardo de Paula Xavier.", "Perícias Médicas – Teoria e Prática", ". Rio de Janeiro: Guanabara Koogan, 2009, 394 p."),
    ("FRANÇA, Genival Veloso de.", "Medicina Legal", ". Rio de Janeiro: Guanabara Koogan, 2017."),
    ("LANDRY, Michel.", "O Psiquiatra no Tribunal", ". São Paulo, Editora Pioneira/ EDUSP, 1981."),
    ("TABORDA, José G. V.; Abdalla-Filho, Elias; Chalub, Miguel.", "Psiquiatria Forense", ". Porto Alegre: Artmed, 3ª Edição 2016."),
    ("VANRELL, Jorge Paulete;", "Perícias Médicas Judiciais", ", JH Mizuno, 2013."),
    ("PALOMBA, Guido Arturo.", "Tratado de Psiquiatria Forense Civil e Penal", ". São Paulo: Atheneu, 2003."),
]

ORD = ["1ª", "2ª", "3ª", "4ª", "5ª", "6ª"]

def _ord(i, n, base):
    if n <= 1:
        return f"{base}:"
    pre = ORD[i] if i < len(ORD) else f"{i+1}ª"
    return f"{pre} {base}:"

# ── Tabelas de identificação (Interditando no lugar de Réu, múltiplas partes) ──

def _ident_rows(autores, interditandos):
    cl = G.cell_label; cv = G.cell_val
    rows = ""
    na = len(autores)
    for i, a in enumerate(autores):
        rows += G.row(cl(_ord(i, na, "Parte autora"), "CellId"), cv(a, "P3C", "CellId"))
    ni = len(interditandos)
    for i, it in enumerate(interditandos):
        rows += G.row(cl(_ord(i, ni, "Interditando"), "CellId"), cv(it, "P3C", "CellId"))
    return rows

def build_table1_int(numero, autores, interditandos):
    cols = G.col("CId1") + G.col("CId2")
    return (G.table_open("Table1", cols)
            + G.row(G.cell_label("Autos:", "CellId"), G.cell_val(numero, "P3C", "CellId"))
            + _ident_rows(autores, interditandos)
            + G.table_close())

def build_table3_int(vara, numero, autores, interditandos, data_local):
    cols = G.col("CId1") + G.col("CId2")
    return (G.table_open("Table3", cols)
            + G.row(G.cell_label("Vara:", "CellId"), G.cell_val(vara, "P17C", "CellId"))
            + G.row(G.cell_label("Autos:", "CellId"), G.cell_val(numero, "P3C", "CellId"))
            + _ident_rows(autores, interditandos)
            + G.row(G.cell_label("Data e local da perícia:", "CellId"), G.cell_val(data_local, "P3C", "CellId"))
            + G.row(G.cell_label("Finalidade da perícia:", "CellId"),
                    G.cell_val("Avaliação de interdição e curatela.", "P2C", "CellId"))
            + G.table_close())

# ── Blocos de texto (Metodologia, Presentes, Quesitos) ────────────────────────

def build_metodologia_xml():
    out = ['<text:p text:style-name="P5"><text:span text:style-name="T5"></text:span></text:p>']
    for item in METODOLOGIA:
        out.append(f'<text:p text:style-name="P18">{x(item)}</text:p>')
        out.append('<text:p text:style-name="P18"></text:p>')
    return ''.join(out)

def build_presentes_xml(presentes):
    out = ['<text:p text:style-name="P16"><text:span text:style-name="T5"></text:span></text:p>']
    for linha in (presentes or ["Parte autora:", "Interditando:"]):
        if ":" in linha:
            lbl, rest = linha.split(":", 1)
            out.append(f'<text:p text:style-name="P19"><text:span text:style-name="T2">{x(lbl)}:</text:span>'
                       f'<text:s/>{x(rest.strip())}</text:p>')
        else:
            out.append(f'<text:p text:style-name="P19">{x(linha)}</text:p>')
    out.append('<text:p text:style-name="P5"></text:p>')
    return ''.join(out)

def _quesitos_grupo(out, titulo, lista):
    def p2(t): return f'<text:p text:style-name="P2">{x(t)}</text:p>'
    def emp(): return '<text:p text:style-name="P2"></text:p>'
    out.append(p2(titulo)); out.append(emp())
    if lista:
        for q in lista:
            marca = q.get("letra") or q.get("numero", "")
            e = q.get("enunciado", "")
            sep = ")" if q.get("letra") else ("." if q.get("numero") else "")
            out.append(p2(f"{marca}{sep} {e}".strip() if marca else e))
            out.append(emp()); out.append(p2("Resposta:")); out.append(emp())
    else:
        out.append(p2("Não localizados nos autos.")); out.append(emp())

def build_quesitos_int_xml(q_juizo, q_autor, q_interd):
    out = []
    _quesitos_grupo(out, "Quesitos do juízo:", q_juizo or QUESITOS_JUIZO_PADRAO)
    _quesitos_grupo(out, "Quesitos da parte autora:", q_autor)
    _quesitos_grupo(out, "Quesitos do interditando:", q_interd)
    return ''.join(out)

def build_bibliografia_xml():
    out = ['<text:p text:style-name="P5"><text:span text:style-name="T5"></text:span></text:p>']
    for autor, titulo, resto in BIBLIOGRAFIA:
        out.append(f'<text:p text:style-name="P5">{x(autor)} '
                   f'<text:span text:style-name="T8">{x(titulo)}</text:span>{x(resto)}</text:p>')
        out.append('<text:p text:style-name="P5"></text:p>')
    return ''.join(out)

def _remove_titulo(c, titulo):
    return re.sub(r'<text:p[^>]*><text:span[^>]*>' + re.escape(titulo) + r'</text:span></text:p>',
                  '', c, count=1)

# ── PRINCIPAL ─────────────────────────────────────────────────────────────────

def gerar_odt_interdicao(dados, caminho_saida):
    numero      = dados.get("numero_processo", "")
    vara_full   = dados.get("vara_completa", "")
    data_atual  = dados.get("data_atual", "")
    autores     = dados.get("autores", []) or ([dados["autor"]["nome"]] if dados.get("autor") else [])
    interditandos = dados.get("interditandos", []) or ([dados["interditando"]] if dados.get("interditando") else [])
    historico   = dados.get("historico", "")
    pedido      = dados.get("pedido", "Interdição")
    presentes   = dados.get("presentes", [])
    atestados   = dados.get("atestados", [])
    exames      = dados.get("exames", [])
    q_juizo     = dados.get("quesitos_juizo", []) or QUESITOS_JUIZO_PADRAO
    q_autor     = dados.get("quesitos_autor", [])
    q_interd    = dados.get("quesitos_interditando", [])
    idade       = dados.get("interditando_idade", "") or dados.get("autor_idade", "")
    alertas     = dados.get("alertas", [])
    data_local  = dados.get("data_local_pericia",
                            "[A PREENCHER — verificar nos autos a designação do juiz]")

    if not os.path.exists(G.BASE_ODT):
        raise FileNotFoundError(f"Template base não encontrado: {G.BASE_ODT}")

    with zipfile.ZipFile(G.BASE_ODT) as z:
        content    = z.read('content.xml').decode('utf-8')
        styles     = z.read('styles.xml').decode('utf-8')
        base_files = {n: z.read(n) for n in z.namelist()}

    content = content.replace('</office:automatic-styles>',
                              G.EXTRA_STYLES.strip() + '</office:automatic-styles>')

    # Endereçamento (vara em maiúsculas)
    content = re.sub(
        r'<text:p text:style-name="P1">AO JUÍZO DA.*?</text:p>',
        f'<text:p text:style-name="P1">AO JUÍZO DA <text:s/>{x(vara_full.upper())}.</text:p>',
        content, count=1, flags=re.DOTALL)

    # Data
    content = re.sub(
        r'<text:p text:style-name="P12">.*?Blumenau,.*?</text:p>',
        f'<text:p text:style-name="P12"><text:s text:c="11"/>Blumenau, {x(data_atual)}.</text:p>',
        content, count=1, flags=re.DOTALL)

    # Tabelas de identificação
    content = G.replace_table(content, "Table1", build_table1_int(numero, autores, interditandos))
    content = G.replace_table(content, "Table2", G.build_table2())
    content = G.replace_table(content, "Table3",
                              build_table3_int(vara_full, numero, autores, interditandos, data_local))

    # Metodologia (texto próprio da interdição)
    content = re.sub(
        r'(Metodologia da perícia:</text:span></text:p>)'
        r'.*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Presentes à perícia:)',
        lambda m: m.group(1) + build_metodologia_xml() + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Presentes à perícia (autora(s) + interditando)
    content = re.sub(
        r'(Presentes à perícia:</text:span></text:p>)'
        r'.*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Histórico da doença)',
        lambda m: m.group(1) + build_presentes_xml(presentes) + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Histórico (sem benefícios/períodos)
    hist_new = G.build_historico_xml(historico, None, pedido)
    content = re.sub(
        r'(Histórico da doença \(alegações da parte autora\):</text:span></text:p>)'
        r'.*?'
        r'(<text:p[^>]*><text:span[^>]*>Documentos de importância médica)',
        lambda m: m.group(1) + hist_new + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Remover Benefícios + CAT + Antecedentes + Antecedentes ocupacionais + CNIS
    # (tudo entre o título "Benefícios previdenciários:" e o título "Exame físico:")
    content = re.sub(
        r'<text:p text:style-name="P5"><text:span text:style-name="T1">Benefícios previdenciários:'
        r'.*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Exame físico:)',
        lambda m: m.group(1),
        content, count=1, flags=re.DOTALL)

    # Documentos: Atestados e Exames (remover tabela+título quando vazios)
    if atestados:
        content = G.replace_table(content, "Table5", G.build_table5(atestados))
    else:
        content = G.replace_table(content, "Table5", "")
        content = _remove_titulo(content, "Atestados, declarações e encaminhamentos presentes aos autos:")
    if exames:
        content = G.replace_table(content, "Table6", G.build_table6(exames))
    else:
        content = G.replace_table(content, "Table6", "")
        content = _remove_titulo(content, "Exames complementares:")

    # Exame físico: idade + Table10 (Peso/Altura/IMC em branco)
    idade_str = str(idade) if idade else "___"
    content = re.sub(
        r'<text:p[^>]*>Contava a parte periciada com.*?</text:p>',
        (f'<text:p text:style-name="P2">Contava a parte periciada com '
         f'{x(idade_str)} anos na data do ato pericial.</text:p>'),
        content, count=1, flags=re.DOTALL)
    content = G.replace_table(content, "Table10", G.build_table10())

    # Quesitos (juízo fixo a–g + autora + interditando)
    content = re.sub(
        r'(Quesitos:</text:span></text:p>)'
        r'.*?'
        r'(<text:p[^>]*><text:span[^>]*>Considerações finais:)',
        lambda m: m.group(1) + build_quesitos_int_xml(q_juizo, q_autor, q_interd) + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Considerações finais (texto da interdição)
    content = re.sub(
        r'<text:p[^>]*>Este laudo é constituído de.*?</text:p>',
        (f'<text:p text:style-name="P22">Este laudo é constituído de '
         f'<text:span text:style-name="T2">xxx (xxx) </text:span>'
         f'folhas, prova pericial produzida sobre '
         f'<text:span text:style-name="T2">Avaliação de interdição e curatela</text:span>'
         f'<text:s/>nos autos '
         f'<text:span text:style-name="T2">RT-{x(numero)}</text:span>'
         f'<text:s/>considerando exclusivamente as constatações fáticas resultantes das '
         f'diligências periciais especificamente realizadas. '
         f'<text:span text:style-name="T2">É </text:span>'
         f'<text:s/><text:span text:style-name="T2">vedada a sua utilização em outras '
         f'situações, ainda que como prova emprestada</text:span>, sem a expressa '
         f'concordância deste perito, sob pena de afrontar o disposto na Lei nº 9610 '
         f'de 19/02/1998, com as suas repercussões legais.</text:p>'),
        content, count=1, flags=re.DOTALL)

    # Bibliografia fixa da interdição (substitui a previdenciária, mesmo estilo)
    content = re.sub(
        r'(Bibliografia utilizada:</text:span></text:p>)'
        r'.*?'
        r'(<text:p[^>]*><text:span[^>]*>Responsável por este laudo pericial)',
        lambda m: m.group(1) + build_bibliografia_xml() + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Remover rodapé duplicado do corpo (P35) e artefato PAGE (P36)
    content = re.sub(r'<text:p text:style-name="P35">.*?</text:p>', '', content, count=1, flags=re.DOTALL)
    content = re.sub(r'<text:p text:style-name="P36">.*?</text:p>', '', content, flags=re.DOTALL)

    # Parágrafos vazios residuais após "Responsável"
    content = re.sub(
        r'(pericias@peritodrlino\.com\.br</text:span></text:p>)'
        r'(?:<text:p[^>]*>(?:<text:span[^>]*></text:span>)?</text:p>)+',
        r'\1', content, count=1)

    # Alertas / Observações para o perito
    if alertas:
        alertas_xml = ('<text:p text:style-name="P2Break">'
                       '<text:span text:style-name="T1">OBSERVAÇÕES PARA O PERITO:</text:span></text:p>')
        for a in alertas:
            alertas_xml += f'<text:p text:style-name="P2">• {x(a)}</text:p>'
        content = content.replace('</office:text>', alertas_xml + '</office:text>')

    # Numeração das seções (própria da interdição)
    numeracao = [
        ("Metodologia da perícia:",                                  "1. Metodologia da perícia:"),
        ("Presentes à perícia:",                                     "2. Presentes à perícia:"),
        ("Histórico da doença (alegações da parte autora):",         "3. Histórico da doença (alegações da parte autora):"),
        ("Documentos de importância médica juntados aos autos:",     "4. Documentos de importância médica juntados aos autos:"),
        ("Atestados, declarações e encaminhamentos presentes aos autos:", "4.1. Atestados, declarações e encaminhamentos presentes aos autos:"),
        ("Exames complementares:",                                   "4.2. Exames complementares:"),
        ("Exame físico:",                                            "5. Exame físico:"),
        ("Discussão / Conclusão:",                                   "6. Discussão / Conclusão:"),
        ("Quesitos:",                                                "7. Quesitos:"),
        ("Considerações finais:",                                    "8. Considerações finais:"),
        ("Bibliografia utilizada:",                                  "9. Bibliografia utilizada:"),
        ("Responsável por este laudo pericial:",                     "10. Responsável por este laudo pericial:"),
    ]
    for antigo, novo in numeracao:
        content = re.sub(r'>' + re.escape(antigo) + r'(\s*)</text:span>',
                         r'>' + novo.replace('\\', '\\\\') + r'\1</text:span>',
                         content, count=1)

    # Lista de classificação do IMC: Times → Arial
    content = content.replace(
        '<text:p text:style-name="P23">18,5 – Abaixo do peso',
        '<text:p text:style-name="PImcList">18,5 – Abaixo do peso', 1)

    # Quebra de página: LAUDO PERICIAL (pág 2)
    content = content.replace(
        '<text:p text:style-name="P15"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>',
        '<text:p text:style-name="P15Break"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>', 1)

    # Quebra de página antes de Considerações / Bibliografia / Responsável
    for titulo in ['8. Considerações finais:', '9. Bibliografia utilizada:',
                   '10. Responsável por este laudo pericial:']:
        content = content.replace(
            f'<text:p text:style-name="P5"><text:span text:style-name="T1">{titulo}',
            f'<text:p text:style-name="P5Break"><text:span text:style-name="T1">{titulo}', 1)

    # Header / Footer (idêntico ao previdenciário)
    styles = G.add_header_footer(styles, numero)

    # Validar XML
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        line, col_n = e.position
        ctx = content.split('\n')[line-1][max(0, col_n-100):col_n+200]
        print(f"ERRO XML content.xml linha {line}: {e}\n  Contexto: {ctx[:200]}")
        sys.exit(1)

    # Montar ODT
    manifest = base_files.get('META-INF/manifest.xml', b'').decode('utf-8')
    if 'header_logo.png' not in manifest and os.path.exists(G.LOGO_PATH):
        manifest = manifest.replace(
            '</manifest:manifest>',
            ' <manifest:file-entry manifest:media-type="image/png" '
            'manifest:full-path="Pictures/header_logo.png"/>\n</manifest:manifest>')

    base_files['content.xml']           = content.encode('utf-8')
    base_files['styles.xml']            = styles.encode('utf-8')
    base_files['META-INF/manifest.xml'] = manifest.encode('utf-8')
    if os.path.exists(G.LOGO_PATH):
        with open(G.LOGO_PATH, 'rb') as f:
            base_files['Pictures/header_logo.png'] = f.read()

    with zipfile.ZipFile(caminho_saida, 'w', zipfile.ZIP_DEFLATED) as zout:
        if 'mimetype' in base_files:
            zout.writestr(zipfile.ZipInfo('mimetype'), base_files['mimetype'])
        for name, data in base_files.items():
            if name != 'mimetype':
                zout.writestr(name, data)

    print(f"ODT gerado: {caminho_saida}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 gerar_prelaudo_interdicao.py dados.json saida.odt")
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        dados = json.load(f)
    gerar_odt_interdicao(dados, sys.argv[2])
