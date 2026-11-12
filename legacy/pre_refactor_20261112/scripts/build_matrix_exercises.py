"""Run the five independent teaching examples and export their worked explanations."""
from pathlib import Path
import json,subprocess,sys
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from pypdf import PdfReader
import pypdfium2 as pdfium
from build_member_pdfs import make_styles,markdown_blocks

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/matrix_exercises';CACHE.mkdir(parents=True,exist_ok=True)

def footer(canvas,doc):
    canvas.setFont('Guide',8)
    canvas.drawString(1.9*cm,1.05*cm,'BTL Xử lý ảnh - Ví dụ ma trận và kiểm chứng NumPy')
    canvas.drawRightString(A4[0]-1.9*cm,1.05*cm,str(doc.page))

def main():
    styles=make_styles();records=[]
    for source in sorted((ROOT/'docs/thanh_vien').glob('TV*/MA_TRAN_TINH_TAY.md')):
        code=source.with_name('vi_du_ma_tran.py')
        run=subprocess.run([sys.executable,'-X','utf8',str(code)],capture_output=True,text=True,encoding='utf-8',cwd=ROOT)
        assert run.returncode==0,run.stderr
        (CACHE/(source.parent.name+'.txt')).write_text(run.stdout,encoding='utf-8')
        target=source.with_suffix('.pdf')
        doc=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=1.9*cm,rightMargin=1.9*cm,
                              topMargin=1.6*cm,bottomMargin=1.8*cm,title=source.parent.name+' - Ma tran tinh tay')
        doc.build(markdown_blocks(source.read_text(encoding='utf-8'),source,styles),onFirstPage=footer,onLaterPages=footer)
        reader=PdfReader(target);alltext='\n'.join(p.extract_text() for p in reader.pages)
        assert 'Câu hỏi' in alltext and 'kiểm chứng' in alltext
        pdf=pdfium.PdfDocument(str(target))
        for i,page in enumerate(pdf):
            page.render(scale=1.2).to_pil().save(CACHE/f'{source.parent.name}_{i+1}.png')
        records.append({'member':source.parent.name,'pages':len(reader.pages),'code_passed':True,'pdf':str(target.relative_to(ROOT))})
    assert len(records)==5
    (CACHE/'audit.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(records,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
