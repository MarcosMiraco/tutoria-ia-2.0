
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from pathlib import Path

assets_dir = Path(__file__).parent.parent / 'assets'
source = assets_dir / 'OwaspTop10LLM.pdf'
output_path = assets_dir / 'output.md'


pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = doc_converter.convert(str(source))
doc = result.document

markdown_content = doc.export_to_markdown()

# DESCOMENTE PARA GRAVAR O MARKDOWN DE RESPOSTA NA PASTA ASSETS 
# with open(output_path, 'w', encoding='utf-8') as f:
# 	f.write(markdown_content)

def get_markdown_doc():
		print("RODANDO INGESTAO DE DOCUMENTO...")
		return markdown_content


# CRIAR INGESTAO DE NOVO ARQUIVO A PARTIR DAQUI:--------------------------------





