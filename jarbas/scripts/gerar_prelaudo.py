#!/usr/bin/env python3
"""
Gerador de Pré-Laudo Pericial — ODT
Substitui dados variáveis no XML do template ODT convertido pelo textutil.
Uso: python3 gerar_prelaudo.py dados.json saida.odt
"""
import sys, json, os, zipfile, re

LOGO_PATH = os.path.expanduser("~/.claude/scripts/cabecalho_francisco_lino.png")
BASE_ODT  = os.path.expanduser("~/.claude/scripts/template_base.odt")

# Dimensões reais da página (do styles.xml do template)
# Página: 8.5×11in, margens: left=1in, right=1in → área de texto = 6.5in = 16.51cm
HEADER_WIDTH  = "16.5cm"   # largura do logo = área de texto
HEADER_HEIGHT = "2.7cm"    # altura proporcional ao logo (2826×455px → ratio 6.21:1)

# ── Escape XML ───────────────────────────────────────────────────────────────

def x(s):
    if not s:
        return ''
    return (str(s).replace('&','&amp;').replace('<','&lt;')
                  .replace('>','&gt;').replace('"','&quot;'))

# ── Estilos extras a injetar no automatic-styles do content.xml ───────────────
# P2C / P3C: P2/P3 sem margin-bottom (para uso dentro de células de tabela)
# Colunas com larguras específicas por tabela.

EXTRA_STYLES = """
<style:style style:name="P2C" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:text-align="justify"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt"/>
</style:style>
<style:style style:name="P3C" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:text-align="justify"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt" fo:color="#000000"/>
</style:style>
<style:style style:name="P17C" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:text-align="justify"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt" fo:color="#000000"/>
</style:style>
<style:style style:name="PHon" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:line-height="110%"/>
  <style:text-properties style:font-name="Arial" fo:font-size="11pt"/>
</style:style>
<!-- Cabeçalhos/rótulos das tabelas dos itens 4 e 5 em Arial 11 (variantes 11pt de P15/P5) -->
<style:style style:name="PH11" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:text-align="center"/>
  <style:text-properties style:font-name="Arial" fo:font-size="11.0pt"/>
</style:style>
<style:style style:name="PL11" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:text-align="justify"/>
  <style:text-properties style:font-name="Arial" fo:font-size="11.0pt"/>
</style:style>
<style:style style:name="P15Break" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:text-align="center" fo:break-before="page"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt"/>
</style:style>
<!-- Células: padding mínimo + borda fina preta -->
<style:style style:name="CellN" style:family="table-cell">
  <style:table-cell-properties fo:padding-top="0.005in" fo:padding-bottom="0.005in" fo:padding-left="0.04in" fo:padding-right="0.04in" fo:border="0.5pt solid #000000"/>
</style:style>
<style:style style:name="CellG" style:family="table-cell">
  <style:table-cell-properties fo:padding-top="0.005in" fo:padding-bottom="0.005in" fo:padding-left="0.04in" fo:padding-right="0.04in" fo:border="0.5pt solid #000000" fo:background-color="#c0c0c0"/>
</style:style>
<style:style style:name="CellHon" style:family="table-cell">
  <style:table-cell-properties fo:padding-top="0.02in" fo:padding-bottom="0.02in" fo:padding-left="0.06in" fo:padding-right="0.06in" fo:border="0.5pt solid #c0c0c0"/>
</style:style>
<!-- Células das tabelas de IDENTIFICAÇÃO: fundo branco, bordas cinza (como no modelo) -->
<style:style style:name="CellId" style:family="table-cell">
  <style:table-cell-properties fo:padding-top="0.005in" fo:padding-bottom="0.005in" fo:padding-left="0.04in" fo:padding-right="0.04in" fo:border="0.5pt solid #c0c0c0"/>
</style:style>
<!-- Tabelas -->
<style:style style:name="TableHon" style:family="table">
  <style:table-properties style:width="3.4in" table:align="center"/>
</style:style>
<style:style style:name="ColHon" style:family="table-column">
  <style:table-column-properties style:column-width="3.4in"/>
</style:style>
<style:style style:name="TableFull" style:family="table">
  <style:table-properties style:width="6.5in" table:align="left"/>
</style:style>
<style:style style:name="TablePer" style:family="table">
  <style:table-properties style:width="2.45in" table:align="left"/>
</style:style>
<style:style style:name="TableEfis" style:family="table">
  <style:table-properties style:width="1.9in" table:align="left"/>
</style:style>
<!-- Colunas com largura absoluta (proporções exatas do modelo, total 6.5in) -->
<style:style style:name="CId1" style:family="table-column"><style:table-column-properties style:column-width="1.17in"/></style:style>
<style:style style:name="CId2" style:family="table-column"><style:table-column-properties style:column-width="5.33in"/></style:style>
<style:style style:name="CPer1" style:family="table-column"><style:table-column-properties style:column-width="1.19in"/></style:style>
<style:style style:name="CPer2" style:family="table-column"><style:table-column-properties style:column-width="1.26in"/></style:style>
<style:style style:name="CAt1" style:family="table-column"><style:table-column-properties style:column-width="0.84in"/></style:style>
<style:style style:name="CAt2" style:family="table-column"><style:table-column-properties style:column-width="2.52in"/></style:style>
<style:style style:name="CAt3" style:family="table-column"><style:table-column-properties style:column-width="1.74in"/></style:style>
<style:style style:name="CAt4" style:family="table-column"><style:table-column-properties style:column-width="1.40in"/></style:style>
<style:style style:name="CEx1" style:family="table-column"><style:table-column-properties style:column-width="0.91in"/></style:style>
<style:style style:name="CEx2" style:family="table-column"><style:table-column-properties style:column-width="4.26in"/></style:style>
<style:style style:name="CEx3" style:family="table-column"><style:table-column-properties style:column-width="1.33in"/></style:style>
<style:style style:name="CBen1" style:family="table-column"><style:table-column-properties style:column-width="0.78in"/></style:style>
<style:style style:name="CBen2" style:family="table-column"><style:table-column-properties style:column-width="0.88in"/></style:style>
<style:style style:name="CBen3" style:family="table-column"><style:table-column-properties style:column-width="1.33in"/></style:style>
<style:style style:name="CBen4" style:family="table-column"><style:table-column-properties style:column-width="2.09in"/></style:style>
<style:style style:name="CBen5" style:family="table-column"><style:table-column-properties style:column-width="1.42in"/></style:style>
<style:style style:name="CCat1" style:family="table-column"><style:table-column-properties style:column-width="0.84in"/></style:style>
<style:style style:name="CCat2" style:family="table-column"><style:table-column-properties style:column-width="1.15in"/></style:style>
<style:style style:name="CCat3" style:family="table-column"><style:table-column-properties style:column-width="1.49in"/></style:style>
<style:style style:name="CCat4" style:family="table-column"><style:table-column-properties style:column-width="0.94in"/></style:style>
<style:style style:name="CCat5" style:family="table-column"><style:table-column-properties style:column-width="1.00in"/></style:style>
<style:style style:name="CCat6" style:family="table-column"><style:table-column-properties style:column-width="1.08in"/></style:style>
<style:style style:name="CCnis1" style:family="table-column"><style:table-column-properties style:column-width="1.85in"/></style:style>
<style:style style:name="CCnis2" style:family="table-column"><style:table-column-properties style:column-width="1.55in"/></style:style>
<style:style style:name="CCnis3" style:family="table-column"><style:table-column-properties style:column-width="3.10in"/></style:style>
<style:style style:name="CEfis1" style:family="table-column"><style:table-column-properties style:column-width="0.95in"/></style:style>
<style:style style:name="CEfis2" style:family="table-column"><style:table-column-properties style:column-width="0.95in"/></style:style>
<!-- Lista de classificação do IMC: Arial (não Times) -->
<style:style style:name="PImcList" style:family="paragraph" style:parent-style-name="Standard">
  <style:text-properties style:font-name="Arial" fo:font-size="10pt" fo:color="#333333"/>
</style:style>
<!-- Título com quebra de página antes -->
<style:style style:name="P5Break" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:text-align="justify" fo:break-before="page"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt"/>
</style:style>
<style:style style:name="P2Break" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:text-align="justify" fo:margin-bottom="0.0396in" fo:break-before="page"/>
  <style:text-properties style:font-name="Arial" fo:font-size="12.0pt"/>
</style:style>
"""

# ── Células ───────────────────────────────────────────────────────────────────

def cell_label(texto, cs="CellN"):
    """Label: P2C+T1 (bold+underline, zero margin)"""
    return (f'<table:table-cell table:style-name="{cs}">'
            f'<text:p text:style-name="P2C"><text:span text:style-name="T1">{x(texto)}</text:span></text:p>'
            f'</table:table-cell>')

def cell_val(texto, style="P3C", cs="CellN"):
    return (f'<table:table-cell table:style-name="{cs}">'
            f'<text:p text:style-name="{style}">{x(texto)}</text:p>'
            f'</table:table-cell>')

def cell_header(texto, cs="CellG"):
    """Cabeçalho cinza: PH11+T2 (bold, centrado, fundo cinza, Arial 11)"""
    return (f'<table:table-cell table:style-name="{cs}">'
            f'<text:p text:style-name="PH11"><text:span text:style-name="T2">{x(texto)}</text:span></text:p>'
            f'</table:table-cell>')

def cell_header_white(texto):
    """Cabeçalho branco (CNIS): P15+T2 sem fundo cinza"""
    return cell_header(texto, cs="CellN")

def cell_label_p5(texto):
    """Label alternado da CAT (branco): PL11+T2 (Arial 11)"""
    return (f'<table:table-cell table:style-name="CellN">'
            f'<text:p text:style-name="PL11"><text:span text:style-name="T2">{x(texto)}</text:span></text:p>'
            f'</table:table-cell>')

def row(*cells):
    return '<table:table-row>' + ''.join(cells) + '</table:table-row>'

def col(style="TableColumn1"):
    return f'<table:table-column table:style-name="{style}"/>'

def table_open(name, cols_xml, style="TableFull"):
    return f'<table:table table:name="{name}" table:style-name="{style}">{cols_xml}'

def table_close():
    return '</table:table>'

# ── Tabelas ───────────────────────────────────────────────────────────────────

def build_table1(numero, autor_nome, reu):
    """Tabela topo: Autos / Parte autora / Réu (col label estreita, valor larga)"""
    cols = col("CId1") + col("CId2")
    return (table_open("Table1", cols)
        + row(cell_label("Autos:", "CellId"),        cell_val(numero,     "P3C", "CellId"))
        + row(cell_label("Parte autora:", "CellId"), cell_val(autor_nome, "P3C", "CellId"))
        + row(cell_label("Réu:", "CellId"),          cell_val(reu,        "P2C", "CellId"))
        + table_close())


def build_table2():
    """Honorários — tabela menor, centralizada, espaçamento reduzido (PHon = Arial 10pt)."""
    dados = [
        ("Banco: ",      "Caixa Econômica Federal – Código 104"),
        ("Agência: ",    "3954"),
        ("Operação: ",   "1288"),
        ("Conta: ",      "000809763656-3"),
        ("Favorecido: ", "Francisco Salvador Brod Lino"),
        ("CPF: ",        "571.906.150-91"),
    ]
    linhas = ''.join(
        f'<text:p text:style-name="PHon"><text:span text:style-name="T2">{x(lbl)}</text:span>{x(val)}</text:p>'
        for lbl, val in dados
    )
    cel = f'<table:table-cell table:style-name="CellHon">{linhas}</table:table-cell>'
    return (f'<table:table table:name="Table2" table:style-name="TableHon">'
            f'<table:table-column table:style-name="ColHon"/>'
            f'<table:table-row>{cel}</table:table-row>'
            f'</table:table>')


def build_table3(vara, numero, autor_nome, reu, data_local_pericia):
    """LAUDO PERICIAL: todas as linhas com 2 colunas (label | valor)."""
    cols = col("CId1") + col("CId2")
    return (table_open("Table3", cols)
        + row(cell_label("Vara:", "CellId"),                  cell_val(vara,               "P17C", "CellId"))
        + row(cell_label("Autos:", "CellId"),                 cell_val(numero,             "P3C", "CellId"))
        + row(cell_label("Parte autora:", "CellId"),          cell_val(autor_nome,         "P3C", "CellId"))
        + row(cell_label("Réu:", "CellId"),                   cell_val(reu,                "P2C", "CellId"))
        + row(cell_label("Data e local da perícia:", "CellId"),cell_val(data_local_pericia, "P3C", "CellId"))
        + row(cell_label("Finalidade da perícia:", "CellId"), cell_val(
            "Verificação de doença e grau de incapacidade.", "P2C", "CellId"))
        + table_close())


def build_table4(periodos):
    """Períodos de benefício: tabela pequena à esquerda, 2 colunas, sem cabeçalho."""
    cols = col("CPer1") + col("CPer2")
    rows = ''
    for p in (periodos or []):
        rows += row(cell_val(p.get("inicio",""), "P20"),
                    cell_val(p.get("fim",""),    "P20"))
    if not rows:
        rows = row(cell_val("Não localizado","P20"), cell_val("","P20"))
    return (f'<table:table table:name="Table4" table:style-name="TablePer">'
            + cols + rows + table_close())


def build_table5(atestados):
    """Atestados: 4 colunas com larguras do modelo."""
    cols = col("CAt1") + col("CAt2") + col("CAt3") + col("CAt4")
    titulo = (f'<table:table-row>'
              f'<table:table-cell table:style-name="CellG" table:number-columns-spanned="4">'
              f'<text:p text:style-name="PH11"><text:span text:style-name="T2">'
              f'ATESTADOS E DECLARAÇÕES</text:span></text:p>'
              f'</table:table-cell>'
              f'<table:covered-table-cell/><table:covered-table-cell/><table:covered-table-cell/>'
              f'</table:table-row>')
    cabec = row(cell_header("DATA"), cell_header("MOTIVO"),
                cell_header("MÉDICO"), cell_header("Nº Folha"))
    dados = ''
    for a in (atestados or [{"data":"*","motivo":"Não localizados","medico":"-","folha":""}]):
        dados += row(cell_val(a.get("data","*"), "P20"),
                     cell_val(a.get("motivo",""), "P20"),
                     cell_val(a.get("medico","-"), "P20"),
                     cell_val(a.get("folha",""), "P20"))
    return table_open("Table5", cols) + titulo + cabec + dados + table_close()


def build_table6(exames):
    """Exames: 3 colunas com larguras do modelo (CONCLUSÃO em célula mesclada)."""
    cols = col("CEx1") + col("CEx2") + col("CEx3")
    cabec = row(cell_header("DATA "), cell_header("EXAME"), cell_header("Nº Folha"))
    dados = ''
    for ex in (exames or []):
        dados += row(cell_val(ex.get("data",""), "P20"),
                     cell_val(ex.get("exame",""), "P20"),
                     cell_val(ex.get("folha",""), "P20"))
        conclusao = ex.get("conclusao","")
        if conclusao:
            linhas = [l.strip() for l in conclusao.split(". ") if l.strip()]
            linhas_xml = ''.join(
                f'<text:p text:style-name="P21">{x(l + ("." if not l.endswith(".") else ""))}</text:p>'
                for l in linhas
            ) + '<text:p text:style-name="P21"></text:p>'
            cel_c = (f'<table:table-cell table:style-name="CellN" table:number-columns-spanned="3">'
                     f'<text:p text:style-name="PL11"><text:span text:style-name="T2">CONCLUSÃO</text:span></text:p>'
                     f'{linhas_xml}</table:table-cell>'
                     f'<table:covered-table-cell/><table:covered-table-cell/>')
            dados += f'<table:table-row>{cel_c}</table:table-row>'
    if not dados:
        dados = row(cell_val("Não localizados nos autos.","P20"),
                    cell_val("","P20"), cell_val("","P20"))
    return table_open("Table6", cols) + cabec + dados + table_close()


def build_table7(beneficios):
    """Benefícios: 5 colunas com larguras do modelo."""
    cols = col("CBen1") + col("CBen2") + col("CBen3") + col("CBen4") + col("CBen5")
    titulo = (f'<table:table-row>'
              f'<table:table-cell table:style-name="CellG" table:number-columns-spanned="5">'
              f'<text:p text:style-name="PH11"><text:span text:style-name="T2">'
              f'BENEFÍCIOS PREVIDENCIÁRIOS</text:span></text:p>'
              f'</table:table-cell>'
              f'<table:covered-table-cell/><table:covered-table-cell/>'
              f'<table:covered-table-cell/><table:covered-table-cell/>'
              f'</table:table-row>')
    cabec = row(cell_header("DIB"), cell_header("DCB"), cell_header("Nº BENEFICIO"),
                cell_header("ESPÉCIE"), cell_header("Nº Folha"))
    dados = ''
    for b in (beneficios or []):
        dados += row(cell_val(b.get("dib",""), "P20"),
                     cell_val(b.get("dcb",""), "P20"),
                     cell_val(b.get("nb",""), "P20"),
                     cell_val(b.get("especie",""), "P20"),
                     cell_val(b.get("folha",""), "P20"))
    if not dados:
        dados = row(*[cell_val("Não localizado" if i==0 else "","P20") for i in range(5)])
    return table_open("Table7", cols) + titulo + cabec + dados + table_close()


def build_table8(cat):
    """CAT: 6 colunas alternando label/valor (larguras do modelo)."""
    cols = (col("CCat1") + col("CCat2") + col("CCat3") +
            col("CCat4") + col("CCat5") + col("CCat6"))
    if not cat:
        return (table_open("Table8", cols)
                + row(cell_val("Não localizada nos autos.","P21"),
                      *[cell_val("","P21") for _ in range(5)])
                + table_close())
    row1 = row(
        cell_label_p5("Emitente"),
        cell_val(cat.get("empregador",""), "P21"),
        cell_label_p5("Data do Acidente"),
        cell_val(cat.get("data_acidente",""), "P21"),
        cell_label_p5("Nº Folha"),
        cell_val(cat.get("folha",""), "P21"),
    )
    # Linha 2: label(span2) | valor(span1) | label(span1) | valor(span2)
    cel_pc = (f'<table:table-cell table:style-name="CellN" table:number-columns-spanned="2">'
              f'<text:p text:style-name="PL11"><text:span text:style-name="T2">'
              f'Parte(s) do Corpo Atingida(s)</text:span></text:p>'
              f'</table:table-cell><table:covered-table-cell/>')
    cel_pcv = cell_val(cat.get("partes_corpo",""), "P21")
    cel_ag = cell_label_p5("Agente Causador")
    cel_agv = (f'<table:table-cell table:style-name="CellN" table:number-columns-spanned="2">'
               f'<text:p text:style-name="P21">{x(cat.get("agente",""))}</text:p>'
               f'</table:table-cell><table:covered-table-cell/>')
    row2 = f'<table:table-row>{cel_pc}{cel_pcv}{cel_ag}{cel_agv}</table:table-row>'
    sit = cat.get("situacao","")
    row3_cel = (f'<table:table-cell table:style-name="CellN" table:number-columns-spanned="6">'
                f'<text:p text:style-name="PL11">'
                f'<text:span text:style-name="T2">Situação Geradora do Acidente ou Doença:</text:span>'
                f'<text:span text:style-name="T6"><text:s/>{x(sit)}</text:span>'
                f'</text:p></table:table-cell>'
                f'<table:covered-table-cell/><table:covered-table-cell/>'
                f'<table:covered-table-cell/><table:covered-table-cell/>'
                f'<table:covered-table-cell/>')
    row3 = f'<table:table-row>{row3_cel}</table:table-row>'
    return table_open("Table8", cols) + row1 + row2 + row3 + table_close()


def build_table9(cnis):
    """CNIS: 3 colunas com larguras do modelo (cabeçalho branco, como no modelo)."""
    cols = col("CCnis1") + col("CCnis2") + col("CCnis3")
    cabec = row(cell_header_white("Período"), cell_header_white("Função"),
                cell_header_white("Empresa"))
    dados = ''
    for c in (cnis or [{"periodo":"","funcao":"CNIS não localizado","empresa":""}]):
        dados += row(cell_val(c.get("periodo",""), "P20"),
                     cell_val(c.get("funcao","Não localizado"), "P20"),
                     cell_val(c.get("empresa",""), "P20"))
    return table_open("Table9", cols) + cabec + dados + table_close()


def build_table10():
    """Exame físico: 2 colunas, label estreita, valor larga."""
    cols = col("CEfis1") + col("CEfis2")
    def r(lbl, val):
        cel_l = (f'<table:table-cell table:style-name="CellN">'
                 f'<text:p text:style-name="P5">{x(lbl)}</text:p>'
                 f'</table:table-cell>')
        cel_r = (f'<table:table-cell table:style-name="CellN">'
                 f'<text:p text:style-name="P15">{x(val)}</text:p>'
                 f'</table:table-cell>')
        return f'<table:table-row>{cel_l}{cel_r}</table:table-row>'
    return (f'<table:table table:name="Table10" table:style-name="TableEfis">'
            + cols
            + r("Peso (kg):",   "")
            + r("Altura (m): ", "")
            + r("IMC:",         "")
            + table_close())


def replace_table(content, name, new_xml):
    if new_xml is None:
        return content
    pat = r'<table:table table:name="' + re.escape(name) + r'"[^>]*>.*?</table:table>'
    result = re.sub(pat, new_xml.replace('\n',''), content, count=1, flags=re.DOTALL)
    if result == content:
        print(f"  AVISO: {name} não substituída")
    return result


# ── Quesitos ──────────────────────────────────────────────────────────────────

def build_quesitos_xml(q_juizo, q_autor, q_reu):
    def p2(t): return f'<text:p text:style-name="P2">{x(t)}</text:p>'
    def emp():  return '<text:p text:style-name="P2"></text:p>'
    out = []
    out.append(p2("Quesitos do juízo:")); out.append(emp())
    for q in (q_juizo or []):
        l = q.get("letra",""); e = q.get("enunciado","")
        out.append(p2(f"{l}) {e}" if l else e))
        out.append(emp()); out.append(p2("Resposta:")); out.append(emp())
    if not q_juizo: out.append(p2("Não localizados nos autos.")); out.append(emp())
    out.append(p2("Quesitos da parte autora:")); out.append(emp())
    for q in (q_autor or []):
        n = q.get("numero",""); e = q.get("enunciado","")
        out.append(p2(f"{n}. {e}" if n else e))
        out.append(emp()); out.append(p2("Resposta:")); out.append(emp())
    if not q_autor: out.append(p2("Não localizados nos autos.")); out.append(emp())
    out.append(p2("Quesitos do réu:")); out.append(emp())
    for q in (q_reu or []):
        n = q.get("numero",""); e = q.get("enunciado","")
        out.append(p2(f"{n}. {e}" if n else e))
        out.append(emp()); out.append(p2("Resposta:")); out.append(emp())
    if not q_reu: out.append(p2("Não localizado nos autos.")); out.append(emp())
    return ''.join(out)


def build_historico_xml(historico, periodos, pedido):
    def p2(t): return f'<text:p text:style-name="P18">{x(t)}</text:p>'
    def emp():  return '<text:p text:style-name="P18"></text:p>'
    out = [emp()]
    for linha in (historico or "[Não localizado nos autos]").split("\n"):
        if linha.strip():
            out.append(p2(linha.strip()))
    if periodos:
        out.append(emp())
        out.append(p2("Esteve em benefício nos seguintes períodos:"))
        out.append(emp())
        out.append(build_table4(periodos))
    if pedido:
        out.append(emp())
        out.append(p2(f"Pedido: {pedido}."))
    out.append(emp())
    return ''.join(out)


# ── Header / Footer ───────────────────────────────────────────────────────────

def add_header_footer(styles_xml, numero):
    # Garantir que a fonte Arial esteja declarada no styles.xml
    if 'svg:font-family="Arial"' not in styles_xml:
        styles_xml = styles_xml.replace(
            '</office:font-face-decls>',
            '<style:font-face style:name="Arial" svg:font-family="Arial"/>'
            '</office:font-face-decls>'
        )

    # Reservar região de cabeçalho/rodapé no page-layout (essencial para o
    # cabeçalho se repetir em TODAS as páginas). Substitui o page-layout inteiro.
    novo_page_layout = (
        '<style:page-layout style:name="Standard">'
        '<style:page-layout-properties fo:page-width="8.5in" fo:page-height="11.0in" '
        'style:print-orientation="portrait" fo:margin-top="0.4in" '
        'fo:margin-bottom="0.5in" fo:margin-left="1.0in" fo:margin-right="1.0in"/>'
        '<style:header-style>'
        '<style:header-footer-properties svg:height="1.1in" fo:min-height="1.1in" '
        'fo:margin-bottom="0.15in"/>'
        '</style:header-style>'
        '<style:footer-style>'
        '<style:header-footer-properties fo:min-height="0.2in" fo:margin-top="0.3in"/>'
        '</style:footer-style>'
        '</style:page-layout>'
    )
    styles_xml = re.sub(
        r'<style:page-layout style:name="Standard">.*?</style:page-layout>',
        novo_page_layout, styles_xml, count=1, flags=re.DOTALL
    )

    # Estilo do rodapé: Arial 10pt, cinza (#808080), negrito, centralizado
    footer_style = (
        '<style:style style:name="FooterPL" style:family="paragraph">'
        '<style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties style:font-name="Arial" fo:font-size="10pt" '
        'fo:color="#808080" fo:font-weight="bold"/>'
        '</style:style>'
    )
    styles_xml = styles_xml.replace('</office:styles>',
                                     footer_style + '</office:styles>')

    # Estilo de frame para o logo
    fr_style = '<style:style style:name="fr1" style:family="graphic"/>'
    styles_xml = styles_xml.replace('</office:automatic-styles>',
                                     fr_style + '</office:automatic-styles>')

    if os.path.exists(LOGO_PATH):
        logo_xml = (
            '<style:header>'
            '<text:p text:style-name="Standard">'
            f'<draw:frame draw:name="LogoCabecalho" draw:style-name="fr1" '
            f'svg:width="{HEADER_WIDTH}" svg:height="{HEADER_HEIGHT}" '
            f'text:anchor-type="as-char">'
            '<draw:image xlink:href="Pictures/header_logo.png" '
            'xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>'
            '</draw:frame>'
            '</text:p>'
            '</style:header>'
        )
    else:
        logo_xml = '<style:header><text:p text:style-name="Standard"/></style:header>'

    footer_xml = (
        '<style:footer>'
        # linha em branco acima do texto do rodapé, para o corpo não colar no rodapé
        # (é conteúdo, então sobrevive a uma reedição no LibreOffice, ao contrário da margem)
        '<text:p text:style-name="FooterPL"/>'
        f'<text:p text:style-name="FooterPL">Laudo Pericial – RT {x(numero)}</text:p>'
        '</style:footer>'
    )

    styles_xml = styles_xml.replace('</style:master-page>',
                                     logo_xml + footer_xml + '</style:master-page>')
    return styles_xml


# ── PRINCIPAL ─────────────────────────────────────────────────────────────────

def gerar_odt(dados, caminho_saida):
    numero           = dados.get("numero_processo", "")
    vara_full        = dados.get("vara_completa", "")
    data_atual       = dados.get("data_atual", "")
    autor            = dados.get("autor", {})
    autor_nome       = autor.get("nome", "")
    autor_rg         = autor.get("rg", "")
    reu              = dados.get("reu", "")
    historico        = dados.get("historico", "")
    pedido           = dados.get("pedido", "")
    periodos         = dados.get("periodos_beneficio", [])
    atestados        = dados.get("atestados", [])
    exames           = dados.get("exames", [])
    beneficios       = dados.get("beneficios", [])
    cat              = dados.get("cat", {})
    cnis             = dados.get("cnis", [])
    q_juizo          = dados.get("quesitos_juizo", [])
    q_autor          = dados.get("quesitos_autor", [])
    q_reu            = dados.get("quesitos_reu", [])
    autor_idade      = dados.get("autor_idade", "")
    alertas          = dados.get("alertas", [])
    data_local_pericia = dados.get("data_local_pericia",
                                   "[A PREENCHER — verificar nos autos a designação do juiz]")

    if not os.path.exists(BASE_ODT):
        raise FileNotFoundError(f"Template base não encontrado: {BASE_ODT}")

    with zipfile.ZipFile(BASE_ODT) as z:
        content    = z.read('content.xml').decode('utf-8')
        styles     = z.read('styles.xml').decode('utf-8')
        base_files = {n: z.read(n) for n in z.namelist()}

    # ── Injetar estilos extras no automatic-styles ────────────────────────────
    content = content.replace('</office:automatic-styles>',
                               EXTRA_STYLES.strip() + '</office:automatic-styles>')

    # ── Substituições de texto (parágrafos inteiros) ──────────────────────────

    # AO JUÍZO DA...
    content = re.sub(
        r'<text:p text:style-name="P1">AO JUÍZO DA.*?</text:p>',
        f'<text:p text:style-name="P1">AO JUÍZO DA <text:s/>{x(vara_full.upper())}.</text:p>',
        content, count=1, flags=re.DOTALL
    )

    # Data (parágrafo P12 com spans internos)
    content = re.sub(
        r'<text:p text:style-name="P12">.*?Blumenau,.*?</text:p>',
        f'<text:p text:style-name="P12"><text:s text:c="11"/>Blumenau, {x(data_atual)}.</text:p>',
        content, count=1, flags=re.DOTALL
    )

    # Presentes à perícia: "Parte autora: NOME – RG ..."
    # No template o parágrafo tem um <text:span> antes do texto "Parte autora:",
    # então a regex precisa casar o conteúdo interno e preservar a estrutura/estilo.
    rg_txt = f" – RG {autor_rg}" if autor_rg else ""
    content = re.sub(
        r'(<text:p text:style-name="P19"><text:span text:style-name="T2">Parte autora:</text:span><text:s/>).*?(</text:p>)',
        lambda m: m.group(1) + x(autor_nome) + x(rg_txt) + '.' + m.group(2),
        content, count=1, flags=re.DOTALL
    )

    # Exame físico — idade
    idade_str = str(autor_idade) if autor_idade else "___"
    content = re.sub(
        r'<text:p[^>]*>Contava a parte periciada com.*?</text:p>',
        (f'<text:p text:style-name="P2">Contava a parte periciada com '
         f'{x(idade_str)} anos na data do ato pericial.</text:p>'),
        content, count=1, flags=re.DOTALL
    )

    # Considerações finais — parágrafo com spans internos
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
        content, count=1, flags=re.DOTALL
    )

    # Remover o rodapé duplicado no CORPO (P35) — o rodapé real fica no styles.xml
    content = re.sub(
        r'<text:p text:style-name="P35">.*?</text:p>', '',
        content, count=1, flags=re.DOTALL
    )
    # Remover o artefato "PAGE N" (P36) gerado na conversão
    content = re.sub(
        r'<text:p text:style-name="P36">.*?</text:p>', '',
        content, flags=re.DOTALL
    )

    # ── Substituição das tabelas ──────────────────────────────────────────────
    content = replace_table(content, "Table1",  build_table1(numero, autor_nome, reu))
    content = replace_table(content, "Table2",  build_table2())
    content = replace_table(content, "Table3",
                             build_table3(vara_full, numero, autor_nome, reu, data_local_pericia))
    # Documentos médicos: quando NÃO houver dados, remover a tabela E o seu título
    # (decisão 14/06/2026 — não deixar tabela com "não localizado"). A numeração 4.x
    # é automática e se reajusta sozinha ao remover o parágrafo de título.
    def remove_titulo(c, titulo):
        return re.sub(
            r'<text:p[^>]*><text:span[^>]*>' + re.escape(titulo) + r'</text:span></text:p>',
            '', c, count=1)

    if atestados:
        content = replace_table(content, "Table5", build_table5(atestados))
    else:
        content = replace_table(content, "Table5", "")
        content = remove_titulo(content, "Atestados, declarações e encaminhamentos presentes aos autos:")

    if exames:
        content = replace_table(content, "Table6", build_table6(exames))
    else:
        content = replace_table(content, "Table6", "")
        content = remove_titulo(content, "Exames complementares:")

    content = replace_table(content, "Table7",  build_table7(beneficios))

    if cat:
        content = replace_table(content, "Table8", build_table8(cat))
    else:
        content = replace_table(content, "Table8", "")
        content = remove_titulo(content, "Dados da CAT – Comunicação de acidente de trabalho:")

    content = replace_table(content, "Table9",  build_table9(cnis))
    content = replace_table(content, "Table10", build_table10())

    # ── Seção de histórico ────────────────────────────────────────────────────
    # Âncora início: após "Histórico da doença...:</text:span></text:p>"
    # Âncora fim: antes de "<text:span...>Documentos de importância médica"
    hist_new = build_historico_xml(historico, periodos, pedido)
    content = re.sub(
        r'(Histórico da doença \(alegações da parte autora\):</text:span></text:p>)'
        r'.*?'
        r'(<text:p[^>]*><text:span[^>]*>Documentos de importância médica)',
        lambda m: m.group(1) + hist_new + m.group(2),
        content, count=1, flags=re.DOTALL
    )

    # ── Bloco de quesitos ─────────────────────────────────────────────────────
    # Âncora início: após "Quesitos:</text:span></text:p>"
    # Âncora fim: antes de "<text:p...><text:span...>Considerações finais:"
    quesitos_new = build_quesitos_xml(q_juizo, q_autor, q_reu)
    content = re.sub(
        r'(Quesitos:</text:span></text:p>)'
        r'.*?'
        r'(<text:p[^>]*><text:span[^>]*>Considerações finais:)',
        lambda m: m.group(1) + quesitos_new + m.group(2),
        content, count=1, flags=re.DOTALL
    )

    # Remover parágrafos vazios residuais após o fim da seção Responsável
    # (evitam página em branco antes das Observações)
    content = re.sub(
        r'(pericias@peritodrlino\.com\.br</text:span></text:p>)'
        r'(?:<text:p[^>]*>(?:<text:span[^>]*></text:span>)?</text:p>)+',
        r'\1',
        content, count=1
    )

    # ── Alertas ───────────────────────────────────────────────────────────────
    if alertas:
        # Observações iniciam no topo de uma nova página (P2Break), título em negrito+sublinhado
        alertas_xml = ('<text:p text:style-name="P2Break">'
                       '<text:span text:style-name="T1">OBSERVAÇÕES PARA O PERITO:</text:span></text:p>')
        for a in alertas:
            alertas_xml += f'<text:p text:style-name="P2">• {x(a)}</text:p>'
        content = content.replace('</office:text>', alertas_xml + '</office:text>')

    # ── Numeração dos títulos das seções ──────────────────────────────────────
    numeracao = [
        ("Metodologia da perícia:",                                  "1. Metodologia da perícia:"),
        ("Presentes à perícia:",                                     "2. Presentes à perícia:"),
        ("Histórico da doença (alegações da parte autora):",         "3. Histórico da doença (alegações da parte autora):"),
        ("Documentos de importância médica juntados aos autos:",     "4. Documentos de importância médica juntados aos autos:"),
        ("Atestados, declarações e encaminhamentos presentes aos autos:", "4.1. Atestados, declarações e encaminhamentos presentes aos autos:"),
        ("Exames complementares:",                                   "4.2. Exames complementares:"),
        ("Benefícios previdenciários:",                              "4.3. Benefícios previdenciários:"),
        ("Dados da CAT – Comunicação de acidente de trabalho:",      "4.4. Dados da CAT – Comunicação de acidente de trabalho:"),
        ("Dados da CAT – Comunicação de Acidente de Trabalho:",      "4.4. Dados da CAT – Comunicação de Acidente de Trabalho:"),
        ("Antecedentes ocupacionais:",                               "5.1. Antecedentes ocupacionais:"),
        ("Antecedentes:",                                            "5. Antecedentes:"),
        ("Exame físico:",                                            "6. Exame físico:"),
        ("Discussão / Conclusão:",                                   "7. Discussão / Conclusão:"),
        ("Quesitos:",                                                "8. Quesitos:"),
        ("Considerações finais:",                                    "9. Considerações finais:"),
        ("Bibliografia utilizada:",                                  "10. Bibliografia utilizada:"),
        ("Responsável por este laudo pericial:",                     "11. Responsável por este laudo pericial:"),
    ]
    # Substituir apenas dentro do span T1 (título), tolerando espaço final
    for antigo, novo in numeracao:
        content = re.sub(
            r'>' + re.escape(antigo) + r'(\s*)</text:span>',
            r'>' + novo.replace('\\', '\\\\') + r'\1</text:span>',
            content, count=1)

    # ── Lista de classificação do IMC: Times → Arial ──────────────────────────
    content = content.replace(
        '<text:p text:style-name="P23">18,5 – Abaixo do peso',
        '<text:p text:style-name="PImcList">18,5 – Abaixo do peso', 1)

    # ── Página 2 inicia com o título "LAUDO PERICIAL" (quebra de página antes) ─
    content = content.replace(
        '<text:p text:style-name="P15"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>',
        '<text:p text:style-name="P15Break"><text:span text:style-name="T1">LAUDO PERICIAL</text:span></text:p>',
        1)

    # ── Quebra de página antes de Considerações / Bibliografia / Responsável ──
    for titulo in ['9. Considerações finais:', '10. Bibliografia utilizada:',
                   '11. Responsável por este laudo pericial:']:
        content = content.replace(
            f'<text:p text:style-name="P5"><text:span text:style-name="T1">{titulo}',
            f'<text:p text:style-name="P5Break"><text:span text:style-name="T1">{titulo}', 1)

    # ── Header / Footer ───────────────────────────────────────────────────────
    styles = add_header_footer(styles, numero)

    # ── Validar XML ───────────────────────────────────────────────────────────
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        line, col_n = e.position
        lines = content.split('\n')
        ctx = lines[line-1][max(0,col_n-100):col_n+200]
        print(f"ERRO XML content.xml linha {line}: {e}\n  Contexto: {ctx[:200]}")
        sys.exit(1)

    # ── Montar ODT ────────────────────────────────────────────────────────────
    manifest = base_files.get('META-INF/manifest.xml', b'').decode('utf-8')
    if 'header_logo.png' not in manifest and os.path.exists(LOGO_PATH):
        manifest = manifest.replace(
            '</manifest:manifest>',
            ' <manifest:file-entry manifest:media-type="image/png" '
            'manifest:full-path="Pictures/header_logo.png"/>\n</manifest:manifest>'
        )

    base_files['content.xml']           = content.encode('utf-8')
    base_files['styles.xml']            = styles.encode('utf-8')
    base_files['META-INF/manifest.xml'] = manifest.encode('utf-8')
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as f:
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
        print("Uso: python3 gerar_prelaudo.py dados.json saida.odt")
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        dados = json.load(f)
    gerar_odt(dados, sys.argv[2])
