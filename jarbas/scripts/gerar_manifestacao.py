#!/usr/bin/env python3
"""
Gerador de Manifestação a Impugnação ao Laudo + Quesitos Complementares — ODT
Padrão do Dr. Francisco Salvador Brod Lino (perito judicial).

Formato fixo (NÃO alterar sem ordem do Dr. Lino):
- Cabeçalho: papel timbrado "FRANCISCO LINO PERÍCIAS" (logo), em todas as páginas.
- Rodapé: número da página, centralizado.
- Linha de endereçamento ao Juízo: SEMPRE toda em MAIÚSCULAS.
- Bloco de qualificação do perito: alinhado à ESQUERDA e JUSTIFICADO, texto normal.
- Ordem do corpo: PRIMEIRO os quesitos complementares, DEPOIS a manifestação.
- Referências bibliográficas: como NOTAS DE RODAPÉ, no ponto da citação.
- Assinatura: centralizada ao final.

Uso: python3 gerar_manifestacao.py dados.json saida.odt

Estrutura do dados.json:
{
  "vara": "1ª VARA ...",            # será forçado a MAIÚSCULAS na linha de endereçamento
  "comarca": "BLUMENAU",
  "estado": "SANTA CATARINA",
  "autos": "....",
  "parte_autora": "...",
  "parte_re": "...",
  "identificacao": "Francisco S. Brod Lino, infra-assinado, Médico Especialista em Medicina Legal e Perícias Médicas, CRM 7532, residente e domiciliado em Blumenau, vem respeitosamente à presença de V. Ex.ª responder os quesitos complementares e se manifestar quanto a impugnação ao Laudo Pericial:",
  "quesitos_titulo": "Quesitos complementares da parte autora (Evento XX):",
  "quesitos": [ {"id":"1","pergunta":"...","resposta": "..." OU [ "texto", {"fn":"Referência..."}, " mais texto" ] } ],
  "manifestacao_titulo": "Manifestação quanto a Impugnação do Laudo",
  "manifestacao_intro": "A parte autora (Evento XX) impugnou ...",
  "manifestacao_itens": [ {"subtitulo":"1. ...","resposta": "..." OU [segments] } ],
  "cidade": "Blumenau",
  "data": "25 de junho de 2026",
  "assinatura": ["Dr. Francisco Lino.","Médico do Trabalho CRM 7532 RQE 18098","Especialista em Medicina Legal e Perícias Médicas"]
}
"""
import sys, json, os, re
from zipfile import ZipFile, ZIP_DEFLATED

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _resolve(name):
    local = os.path.join(SCRIPT_DIR, name)
    if os.path.exists(local):
        return local
    return os.path.expanduser(os.path.join("~/.claude/scripts", name))

LOGO_PATH = _resolve("cabecalho_francisco_lino.png")
BASE_ODT  = _resolve("template_base.odt")

HEADER_WIDTH  = "16.5cm"
HEADER_HEIGHT = "2.7cm"


def x(s):
    if s is None:
        return ''
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
                  .replace('>', '&gt;').replace('"', '&quot;'))


# ── Estilos do corpo (automatic-styles do content.xml) ───────────────────────
BODY_STYLES = """
<style:style style:name="MEnd" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="justify" fo:margin-bottom="0.18in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt" fo:font-weight="bold"/>
</style:style>
<style:style style:name="MLbl" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="start" fo:margin-bottom="0.02in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt"/>
</style:style>
<style:style style:name="MIdent" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="justify" fo:margin-top="0.18in" fo:margin-bottom="0.18in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt"/>
</style:style>
<style:style style:name="MHead" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="start" fo:margin-top="0.16in" fo:margin-bottom="0.10in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt" fo:font-weight="bold"/>
</style:style>
<style:style style:name="MQ" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="justify" fo:margin-top="0.10in" fo:margin-bottom="0.04in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt"/>
</style:style>
<style:style style:name="MResp" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="justify" fo:margin-bottom="0.10in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt"/>
</style:style>
<style:style style:name="MCenter" style:family="paragraph" style:parent-style-name="Standard">
 <style:paragraph-properties fo:text-align="center" fo:margin-top="0.04in" fo:margin-bottom="0.02in"/>
 <style:text-properties style:font-name="Arial" fo:font-size="12pt"/>
</style:style>
<style:style style:name="MFnote" style:family="paragraph" style:parent-style-name="Standard">
 <style:text-properties style:font-name="Arial" fo:font-size="10pt"/>
</style:style>
"""

FOOTER_STYLE = (
    '<style:style style:name="FooterPL" style:family="paragraph">'
    '<style:paragraph-properties fo:text-align="center"/>'
    '<style:text-properties style:font-name="Arial" fo:font-size="10pt" fo:color="#808080"/>'
    '</style:style>'
)


def add_header_footer(styles_xml):
    if 'svg:font-family="Arial"' not in styles_xml:
        styles_xml = styles_xml.replace(
            '</office:font-face-decls>',
            '<style:font-face style:name="Arial" svg:font-family="Arial"/></office:font-face-decls>')

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
        '<style:header-footer-properties fo:min-height="0.2in" fo:margin-top="0.15in"/>'
        '</style:footer-style>'
        '</style:page-layout>'
    )
    styles_xml = re.sub(r'<style:page-layout style:name="Standard">.*?</style:page-layout>',
                        novo_page_layout, styles_xml, count=1, flags=re.DOTALL)

    styles_xml = styles_xml.replace('</office:styles>', FOOTER_STYLE + '</office:styles>')
    fr_style = '<style:style style:name="fr1" style:family="graphic"/>'
    styles_xml = styles_xml.replace('</office:automatic-styles>',
                                    fr_style + '</office:automatic-styles>')

    if os.path.exists(LOGO_PATH):
        logo_xml = (
            '<style:header><text:p text:style-name="Standard">'
            f'<draw:frame draw:name="LogoCabecalho" draw:style-name="fr1" '
            f'svg:width="{HEADER_WIDTH}" svg:height="{HEADER_HEIGHT}" text:anchor-type="as-char">'
            '<draw:image xlink:href="Pictures/header_logo.png" xlink:type="simple" '
            'xlink:show="embed" xlink:actuate="onLoad"/></draw:frame></text:p></style:header>'
        )
    else:
        logo_xml = '<style:header><text:p text:style-name="Standard"/></style:header>'

    footer_xml = ('<style:footer><text:p text:style-name="FooterPL">'
                  '<text:page-number text:select-page="current">1</text:page-number>'
                  '</text:p></style:footer>')

    styles_xml = styles_xml.replace('</style:master-page>',
                                    logo_xml + footer_xml + '</style:master-page>')
    return styles_xml


# ── Construção de runs com notas de rodapé ───────────────────────────────────
class NoteCounter:
    def __init__(self):
        self.n = 0
    def next(self):
        self.n += 1
        return self.n


def render_segments(resposta, counter, label_bold="Resposta: "):
    """Monta o conteúdo de um parágrafo de resposta (com rótulo em negrito e
    eventuais notas de rodapé). resposta pode ser string ou lista de segmentos."""
    runs = []
    if label_bold:
        runs.append(f'<text:span text:style-name="Bold">{x(label_bold)}</text:span>')
    if isinstance(resposta, str):
        resposta = [resposta]
    for seg in resposta:
        if isinstance(seg, dict) and 'fn' in seg:
            i = counter.next()
            runs.append(
                f'<text:note text:id="ftn{i}" text:note-class="footnote">'
                f'<text:note-citation>{i}</text:note-citation>'
                f'<text:note-body><text:p text:style-name="MFnote">{x(seg["fn"])}</text:p>'
                f'</text:note-body></text:note>')
        else:
            runs.append(x(seg))
    return ''.join(runs)


def build_body(d):
    counter = NoteCounter()
    out = []
    # Linha de endereçamento — SEMPRE maiúscula
    end = "AO JUÍZO DA {vara} DA COMARCA DE {comarca} – ESTADO DE {estado}.".format(
        vara=d.get('vara', ''), comarca=d.get('comarca', ''), estado=d.get('estado', '')).upper()
    out.append(f'<text:p text:style-name="MEnd">{x(end)}</text:p>')

    for lbl, key in [("Autos:", "autos"), ("Parte autora:", "parte_autora"), ("Parte ré:", "parte_re")]:
        out.append(f'<text:p text:style-name="MLbl"><text:span text:style-name="Bold">{x(lbl)}</text:span> {x(d.get(key,""))}</text:p>')

    out.append(f'<text:p text:style-name="MIdent">{x(d.get("identificacao",""))}</text:p>')

    # Quesitos complementares (PRIMEIRO)
    if d.get('quesitos'):
        out.append(f'<text:p text:style-name="MHead">{x(d.get("quesitos_titulo","Quesitos complementares:"))}</text:p>')
        for q in d['quesitos']:
            out.append(f'<text:p text:style-name="MQ"><text:span text:style-name="Bold">{x(q["id"])}) </text:span>{x(q["pergunta"])}</text:p>')
            out.append(f'<text:p text:style-name="MResp">{render_segments(q.get("resposta",""), counter)}</text:p>')

    # Manifestação (DEPOIS)
    out.append(f'<text:p text:style-name="MHead">{x(d.get("manifestacao_titulo","Manifestação quanto a Impugnação do Laudo"))}</text:p>')
    if d.get('manifestacao_intro'):
        out.append(f'<text:p text:style-name="MResp">{render_segments(d["manifestacao_intro"], counter, label_bold="")}</text:p>')
    for it in d.get('manifestacao_itens', []):
        if it.get('subtitulo'):
            out.append(f'<text:p text:style-name="MHead">{x(it["subtitulo"])}</text:p>')
        out.append(f'<text:p text:style-name="MResp">{render_segments(it.get("resposta",""), counter)}</text:p>')

    # Fecho
    out.append('<text:p text:style-name="MResp">Por fim, coloco-me à disposição de Vossa Excelência para prestar quaisquer outros esclarecimentos que se ensejarem necessários.</text:p>')
    out.append('<text:p text:style-name="MResp">Nestes termos, pede e espera deferimento.</text:p>')
    out.append(f'<text:p text:style-name="MCenter">{x(d.get("cidade","Blumenau"))}, {x(d.get("data",""))}.</text:p>')
    out.append('<text:p text:style-name="MCenter"></text:p>')
    for i, lin in enumerate(d.get('assinatura', ["Dr. Francisco Lino.", "Médico do Trabalho CRM 7532 RQE 18098", "Especialista em Medicina Legal e Perícias Médicas"])):
        bold = ' text:style-name="Bold"' if i == 0 else ''
        out.append(f'<text:p text:style-name="MCenter"><text:span{bold}>{x(lin)}</text:span></text:p>')

    return ''.join(out)


def gerar_odt(d, caminho_saida):
    z = ZipFile(BASE_ODT)
    files = {n: z.read(n) for n in z.namelist()}
    z.close()

    # content.xml — reusar o cabeçalho (declarações) do template e trocar o corpo
    content = files['content.xml'].decode('utf-8')
    # Inserir estilos do corpo + estilo Bold
    bold_style = '<style:style style:name="Bold" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>'
    content = content.replace('</office:automatic-styles>', BODY_STYLES + bold_style + '</office:automatic-styles>')
    # Substituir todo o conteúdo de office:text
    novo_text = '<office:text>' + build_body(d) + '</office:text>'
    content = re.sub(r'<office:text>.*?</office:text>', lambda m: novo_text, content, count=1, flags=re.DOTALL)
    files['content.xml'] = content.encode('utf-8')

    # styles.xml — cabeçalho/rodapé
    styles = files['styles.xml'].decode('utf-8')
    files['styles.xml'] = add_header_footer(styles).encode('utf-8')

    # manifest + logo
    manifest = files.get('META-INF/manifest.xml', b'').decode('utf-8')
    if 'header_logo.png' not in manifest and os.path.exists(LOGO_PATH):
        manifest = manifest.replace('</manifest:manifest>',
            ' <manifest:file-entry manifest:media-type="image/png" '
            'manifest:full-path="Pictures/header_logo.png"/>\n</manifest:manifest>')
        files['META-INF/manifest.xml'] = manifest.encode('utf-8')
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as f:
            files['Pictures/header_logo.png'] = f.read()

    with ZipFile(caminho_saida, 'w', ZIP_DEFLATED) as out:
        # mimetype primeiro, sem compressão
        if 'mimetype' in files:
            out.writestr('mimetype', files.pop('mimetype'), compress_type=__import__('zipfile').ZIP_STORED)
        for n, data in files.items():
            out.writestr(n, data)
    print('Documento salvo:', caminho_saida)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Uso: python3 gerar_manifestacao.py dados.json saida.odt'); sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        dados = json.load(f)
    gerar_odt(dados, sys.argv[2])
