from typing import Type, Dict
from bs4 import BeautifulSoup
from typing import Protocol, List
from llama_index.core.schema import Document
import re
import unicodedata
from ingestion.utils import extract_header_content

from typing import Type, Dict, Protocol, List
from llama_index.core.schema import Document
from bs4 import BeautifulSoup
import re
import unicodedata

# from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama


class DocumentTransformStrategy(Protocol):
    def __call__(self, doc: Document, **kwargs) -> Document:
        ...

class DocumentTransformRegistry:
    _registry: Dict[str, Type[DocumentTransformStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(transform_cls: Type[DocumentTransformStrategy]):
            cls._registry[name] = transform_cls
            return transform_cls
        return decorator

    @classmethod
    def create(cls, name: str) -> DocumentTransformStrategy:
        if name not in cls._registry:
            raise ValueError(f"Document transform '{name}' not registered")
        return cls._registry[name]()


def apply_document_transforms(documents: List[Document], transform_names: List[str]) -> List[Document]:
    """
    Aplica os transformers em ordem, documento por documento.
    """
    # Instancia transformers
    transformers = [DocumentTransformRegistry.create(name) for name in transform_names]

    processed_documents = []
    for doc in documents:
        for transformer in transformers:
            doc = transformer(doc)  # cada doc passa sequencialmente por todos
        processed_documents.append(doc)

    return processed_documents


@DocumentTransformRegistry.register("mte-header")
class MTEHeaderDocumentExtractor:

    def __call__(self, doc: Document, **kwargs) -> Document:
        """
        Extrai campos do header do CCT e atualiza metadata.
        """
        from ingestion.utils import extract_fields

        # Extrai metadata do header
        metadata = extract_fields(doc.text)

        # Atualiza metadata existente
        doc.metadata.update(metadata)

        return doc
    
@DocumentTransformRegistry.register("llm-category-extractor")
class LLMCategoryMetadataExtractor:
    def __init__(self):
        # Inicializa o LLM predictor
        # self.llm = OpenAI(model="gpt-4o-mini", temperature=0, max_output_tokens=100)
        self.llm = Ollama(model="qwen2.5:7b", temperature=0, request_timeout=60.0)
        self.allowed_categories = [
            "saúde", "varejo", "indústria", "educação", "hotelaria",
            "transporte", "financeiro", "tecnologia", "alimentação", "geral"
        ]
    def __call__(self, doc: Document, **kwargs) -> Document:
        """
        Extrai o segmento de mercado (varejo, saúde, indústria) do header da CCT
        e atualiza a metadata do documento.
        """

        # Extrai apenas o header do CCT
        header_text = extract_header_content(doc.text)
      
        # Aqui você pode usar LLM ou regras simples para determinar o segmento
        segment = self._extract_segment_from_header(header_text)

        # Atualiza metadata
        if segment:
            doc.metadata["segment"] = segment

        return doc
    def _extract_segment_from_header(self, header_text: str) -> str:
        # Prompt explícito pedindo apenas uma categoria válida
        prompt = f"""
        Analise o seguinte cabeçalho de convenção coletiva de trabalho e
        identifique a categoria econômica mais apropriada.

        Categorias permitidas: {', '.join(self.allowed_categories)}.

        Responda APENAS com o nome da categoria mais adequada, sem explicações.

        Cabeçalho:
        \"\"\"{header_text}\"\"\"
        """

        try:
            response = self.llm.complete(prompt)
            if response.text in self.allowed_categories:
                return response.text
            else:
                return "geral"  # fallback
        except Exception as e:
            print(f"[LLMCategoryMetadataExtractor] erro: {e}")
            return "geral"
        
@DocumentTransformRegistry.register("html-sanitizer")
class HtmlSanitizer:

    def __call__(self, doc: Document) -> Document:
        if not self._looks_like_html(doc.text):
            return doc

        cleaned = self._clean_html(doc.text)
        return Document(text=cleaned, metadata=doc.metadata)

    @staticmethod
    def _looks_like_html(text: str) -> bool:
        if not text:
            return False
        lowered = text.lower()
        return any(tag in lowered for tag in ("<html", "<body", "<script", "<div"))

    @staticmethod
    def _clean_html(text: str) -> str:
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n").strip()


@DocumentTransformRegistry.register("normalize")
class NormalizeDocumentTransformer:

    def __call__(self, doc: Document) -> Document:
        text = self._normalize_unicode(doc.text)
        text = self._normalize_whitespace(text)
        return Document(text=text, metadata=doc.metadata)

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


@DocumentTransformRegistry.register("obsidian-sanitizer")
class ObsidianSanitizer:

    def __call__(self, doc: Document) -> Document:
        text = doc.text
        text = self._remove_frontmatter_keys(text, keys=["cssclasses"])
        text = self._remove_callout_lines(text)
        text = self._clean_blockquote_bullets(text)
        text = self._remove_span_tags(text)
        return Document(text=text, metadata=doc.metadata)

    @staticmethod
    def _remove_frontmatter_keys(text: str, keys: list) -> str:
        """Remove chaves específicas do frontmatter YAML."""
        in_frontmatter = False
        result = []
        skip_block = False
        i = 0
        lines = text.splitlines()

        for i, line in enumerate(lines):
            if i == 0 and line.strip() == "---":
                in_frontmatter = True
                result.append(line)
                continue
            if in_frontmatter and line.strip() == "---":
                in_frontmatter = False
                skip_block = False
                result.append(line)
                continue
            if in_frontmatter:
                if any(line.startswith(k + ":") for k in keys):
                    skip_block = True
                    continue
                if skip_block and line.startswith("  "):
                    continue
                else:
                    skip_block = False
            result.append(line)

        return "\n".join(result)

    @staticmethod
    def _remove_callout_lines(text: str) -> str:
        """Remove linhas com sintaxe >[!...] do Obsidian."""
        return re.sub(r"^>{1,}\s*\[!.*?\]\s*$", "", text, flags=re.MULTILINE)

    @staticmethod
    def _clean_blockquote_bullets(text: str) -> str:
        """Converte '>>- item' em '- item'."""
        return re.sub(r"^>{1,}\s*-\s*", "- ", text, flags=re.MULTILINE)

    @staticmethod
    def _remove_span_tags(text: str) -> str:
        """Remove tags <span> mantendo o texto interno."""
        return re.sub(r"<span[^>]*>(.*?)</span>", r"\1", text)