#!/usr/bin/env python3
"""
Gerador de Pré-Laudo Pericial SECURITÁRIO (seguro / invalidez por acidente pessoal) — ODT
Reaproveita EXATAMENTE a formatação do pré-laudo previdenciário (mesmo template_base.odt,
estilos, fontes, tamanhos, títulos e espaçamentos). Muda apenas a ESTRUTURA:
- Réu é seguradora privada (ex.: Icatu Seguros S/A); aceita vários autores e réus
- Finalidade: "Verificação de doença e quantum incapacitante."
- Metodologia própria (lesão permanente/temporária; exame clínico; avaliação da invalidez/tabela)
- Remove Benefícios, CAT, CNIS e Antecedentes ocupacionais
- Exame físico e Discussão/Conclusão (graduação SUSEP) ficam em branco (perícia)
- Quesitos transcritos dos autos (juízo, autora, réu/seguradora); nada é pré-carregado
- Bibliografia e Considerações = padrão do template (ortopédica/previdenciária; "quantum incapacitante")

Uso: python3 gerar_prelaudo_securitaria.py dados.json saida.odt
"""
import sys, json, os, zipfile, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_prelaudo as G
x = G.x

METODOLOGIA = [
    "1.1 Realização de uma entrevista com a parte autora, definindo sua lesão, se tal lesão é permanente ou temporária, antecedentes pessoais, hábitos de vida, sendo facultada a presença dos assistentes técnicos (médicos) das partes, eventualmente nomeados nos autos.",
    "1.2 Exame clínico com a presença do autor e perito do juízo, sendo também facultado o acompanhamento desta fase pelos assistentes técnicos (médicos).",
    "1.3 Avaliação técnica sobre a invalidez eventualmente apresentada em relação à lesão especificada e quantificação baseada na tabela específica.",
]

ORD_F = ["1ª", "2ª", "3ª", "4ª", "5ª", "6ª"]
ORD_M = ["1º", "2º", "3º", "4º", "5º", "6º"]

def _label(i, n, base, ordlist):
    if n <= 1:
        return f"{base}:"
    pre = ordlist[i] if i < len(ordlist) else f"{i+1}º"
    return f"{pre} {base}:"

# ── Tabelas de identificação (Réu = seguradora) ───────────────────────────────

def _ident_rows(autores, reus):
    cl = G.cell_label; cv = G.cell_val
    rows = ""
    na = len(autores)
    for i, a in enumerate(autores):
        rows += G.row(cl(_label(i, na, "Parte autora", ORD_F), "CellId"), cv(a, "P3C", "CellId"))
    nr = len(reus)
    for i, r in enumerate(reus):
        rows += G.row(cl(_label(i, nr, "Réu", ORD_M), "CellId"), cv(r, "P3C", "CellId"))
    return rows

def build_table1_sec(numero, autores, reus):
    cols = G.col("CId1") + G.col("CId2")
    return (G.table_open("Table1", cols)
            + G.row(G.cell_label("Autos:", "CellId"), G.cell_val(numero, "P3C", "CellId"))
            + _ident_rows(autores, reus)
            + G.table_close())

def build_table3_sec(vara, numero, autores, reus, data_local):
    cols = G.col("CId1") + G.col("CId2")
    return (G.table_open("Table3", cols)
            + G.row(G.cell_label("Vara:", "CellId"), G.cell_val(vara, "P17C", "CellId"))
            + G.row(G.cell_label("Autos:", "CellId"), G.cell_val(numero, "P3C", "CellId"))
            + _ident_rows(autores, reus)
            + G.row(G.cell_label("Data e local da perícia:", "CellId"), G.cell_val(data_local, "P3C", "CellId"))
            + G.row(G.cell_label("Finalidade da perícia:", "CellId"),
                    G.cell_val("Verificação de doença e quantum incapacitante.", "P2C", "CellId"))
            + G.table_close())

# ── Blocos de texto ───────────────────────────────────────────────────────────

def build_metodologia_xml():
    out = ['<text:p text:style-name="P5"><text:span text:style-name="T5"></text:span></text:p>']
    for item in METODOLOGIA:
        out.append(f'<text:p text:style-name="P18">{x(item)}</text:p>')
        out.append('<text:p text:style-name="P18"></text:p>')
    return ''.join(out)

def build_presentes_xml(presentes):
    out = ['<text:p text:style-name="P16"><text:span text:style-name="T5"></text:span></text:p>']
    for linha in (presentes or ["Parte autora:"]):
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

def build_quesitos_sec_xml(q_juizo, q_autor, q_reu):
    out = []
    _quesitos_grupo(out, "Quesitos do juízo:", q_juizo)
    _quesitos_grupo(out, "Quesitos da parte autora:", q_autor)
    _quesitos_grupo(out, "Quesitos do réu:", q_reu)
    return ''.join(out)

def _remove_titulo(c, titulo):
    return re.sub(r'<text:p[^>]*><text:span[^>]*>' + re.escape(titulo) + r'</text:span></text:p>',
                  '', c, count=1)

# ── PRINCIPAL ─────────────────────────────────────────────────────────────────

def gerar_odt_securitaria(dados, caminho_saida):
    numero      = dados.get("numero_processo", "")
    vara_full   = dados.get("vara_completa", "")
    data_atual  = dados.get("data_atual", "")
    autores     = dados.get("autores", []) or ([dados["autor"]["nome"]] if dados.get("autor") else [])
    reus        = dados.get("reus", []) or ([dados["reu"]] if dados.get("reu") else [])
    historico   = dados.get("historico", "")
    pedido      = dados.get("pedido", "Complementação da indenização")
    presentes   = dados.get("presentes", [])
    atestados   = dados.get("atestados", [])
    exames      = dados.get("exames", [])
    q_juizo     = dados.get("quesitos_juizo", [])
    q_autor     = dados.get("quesitos_autor", [])
    q_reu       = dados.get("quesitos_reu", [])
    idade       = dados.get("autor_idade", "") or dados.get("periciado_idade", "")
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

    # Endereçamento + data
    content = re.sub(
        r'<text:p text:style-name="P1">AO JUÍZO DA.*?</text:p>',
        f'<text:p text:style-name="P1">AO JUÍZO DA <text:s/>{x(vara_full.upper())}.</text:p>',
        content, count=1, flags=re.DOTALL)
    content = re.sub(
        r'<text:p text:style-name="P12">.*?Blumenau,.*?</text:p>',
        f'<text:p text:style-name="P12"><text:s text:c="11"/>Blumenau, {x(data_atual)}.</text:p>',
        content, count=1, flags=re.DOTALL)

    # Identificação
    content = G.replace_table(content, "Table1", build_table1_sec(numero, autores, reus))
    content = G.replace_table(content, "Table2", G.build_table2())
    content = G.replace_table(content, "Table3",
                              build_table3_sec(vara_full, numero, autores, reus, data_local))

    # Metodologia própria
    content = re.sub(
        r'(Metodologia da perícia:</text:span></text:p>).*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Presentes à perícia:)',
        lambda m: m.group(1) + build_metodologia_xml() + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Presentes
    content = re.sub(
        r'(Presentes à perícia:</text:span></text:p>).*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Histórico da doença)',
        lambda m: m.group(1) + build_presentes_xml(presentes) + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Histórico (sem benefícios/períodos)
    hist_new = G.build_historico_xml(historico, None, pedido)
    content = re.sub(
        r'(Histórico da doença \(alegações da parte autora\):</text:span></text:p>).*?'
        r'(<text:p[^>]*><text:span[^>]*>Documentos de importância médica)',
        lambda m: m.group(1) + hist_new + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Remover Benefícios + CAT + Antecedentes + Antecedentes ocupacionais + CNIS
    content = re.sub(
        r'<text:p text:style-name="P5"><text:span text:style-name="T1">Benefícios previdenciários:.*?'
        r'(<text:p text:style-name="P5"><text:span text:style-name="T1">Exame físico:)',
        lambda m: m.group(1),
        content, count=1, flags=re.DOTALL)

    # Documentos
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

    # Exame físico: idade + Table10 (em branco)
    idade_str = str(idade) if idade else "___"
    content = re.sub(
        r'<text:p[^>]*>Contava a parte periciada com.*?</text:p>',
        (f'<text:p text:style-name="P2">Contava a parte periciada com '
         f'{x(idade_str)} anos na data do ato pericial.</text:p>'),
        content, count=1, flags=re.DOTALL)
    content = G.replace_table(content, "Table10", G.build_table10())

    # Quesitos (transcritos dos autos)
    content = re.sub(
        r'(Quesitos:</text:span></text:p>).*?'
        r'(<text:p[^>]*><text:span[^>]*>Considerações finais:)',
        lambda m: m.group(1) + build_quesitos_sec_xml(q_juizo, q_autor, q_reu) + m.group(2),
        content, count=1, flags=re.DOTALL)

    # Considerações finais (mesmo assunto do previdenciário: "doença e quantum incapacitante")
    content = re.sub(
        r'<text:p[^>]*>Este laudo é constituído de.*?</text:p>',
        (f'<text:p text:style-name="P22">Este laudo é constituído de '
         f'<text:span text:style-name="T2">xxx (xxx) </text:span>'
         f'folhas, prova pericial produzida sobre '
         f'<text:span text:style-name="T2">doença e quantum incapacitante</text:span>'
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

    # (Bibliografia: mantém o padrão do template — ortopédica/previdenciária)

    # Remover rodapé duplicado (P35) e artefato PAGE (P36)
    content = re.sub(r'<text:p text:style-name="P35">.*?</text:p>', '', content, count=1, flags=re.DOTALL)
    content = re.sub(r'<text:p text:style-name="P36">.*?</text:p>', '', content, flags=re.DOTALL)

    content = re.sub(
        r'(pericias@peritodrlino\.com\.br</text:span></text:p>)'
        r'(?:<text:p[^>]*>(?:<text:span[^>]*></text:span>)?</text:p>)+',
        r'\1', content, count=1)

    # Alertas
    if alertas:
        alertas_xml = ('<text:p text:style-name="P2Break">'
                       '<text:span text:style-name="T1">OBSERVAÇÕES PARA O PERITO:</text:span></text:p>')
        for a in alertas:
            alertas_xml += f'<text:p text:style-name="P2">• {x(a)}</text:p>'
        content = content.replace('</office:text>', alertas_xml + '</office:text>')

    # Numeração própria (igual à interdição: sem Antecedentes)
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

    content = content.replace(
        '<text:p text:style-name="P23">18,5 – Abaixo do peso',
        '<text:p text:style-name="PImcList">18,5 – Abaixo do peso', 1)
    content = content.replace(
        '<text:p text:style-name="P15"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>',
        '<text:p text:style-name="P15Break"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>', 1)
    for titulo in ['8. Considerações finais:', '9. Bibliografia utilizada:',
                   '10. Responsável por este laudo pericial:']:
        content = content.replace(
            f'<text:p text:style-name="P5"><text:span text:style-name="T1">{titulo}',
            f'<text:p text:style-name="P5Break"><text:span text:style-name="T1">{titulo}', 1)

    styles = G.add_header_footer(styles, numero)

    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        line, col_n = e.position
        ctx = content.split('\n')[line - 1][max(0, col_n - 100):col_n + 200]
        print(f"ERRO XML content.xml linha {line}: {e}\n  Contexto: {ctx[:200]}")
        sys.exit(1)

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
        print("Uso: python3 gerar_prelaudo_securitaria.py dados.json saida.odt")
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        dados = json.load(f)
    gerar_odt_securitaria(dados, sys.argv[2])
