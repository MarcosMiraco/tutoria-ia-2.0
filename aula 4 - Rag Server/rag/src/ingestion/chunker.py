from typing import Type, Dict
from typing import Protocol
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.node_parser import SentenceSplitter, NodeParser
import re
from typing import List, ClassVar

class ChunkerStrategy(Protocol):
    def get_transform(self):
        ...

class ChunkerRegistry:
    _registry: Dict[str, Type[ChunkerStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(chunker_cls: Type[ChunkerStrategy]):
            cls._registry[name] = chunker_cls
            return chunker_cls
        return decorator

    @classmethod
    def create(cls, name: str) -> ChunkerStrategy:
        if name not in cls._registry:
            raise ValueError(f"Chunker '{name}' not registered")
        return cls._registry[name]()


@ChunkerRegistry.register("cct")
class CctDocumentChunker:
    def get_transform(self):
        return CCTClauseParser(
            max_tokens=1800
        )



class CCTClauseParser(NodeParser):
    max_tokens: int = 1800
    fallback_chunk_size: int = 1024
    fallback_overlap: int = 50

    CLAUSE_REGEX: ClassVar[re.Pattern] = re.compile(
        r"(CLÁUSULA\s+[A-ZÁÉÍÓÚÇ]+.*?)(?=CLÁUSULA\s+[A-ZÁÉÍÓÚÇ]+|$)",
        re.DOTALL | re.IGNORECASE
    )

    @property
    def fallback_splitter(self):
        return SentenceSplitter(
            chunk_size=self.fallback_chunk_size,
            chunk_overlap=self.fallback_overlap
        )

    def _parse_nodes(
        self,
        nodes: List[BaseNode],
        **kwargs,
    ) -> List[BaseNode]:
        output_nodes: List[BaseNode] = []

        for node in nodes:
            text = node.get_content()

            annex_match = re.search(r"\bANEXOS\b", text, re.IGNORECASE)

            annex_text = None
            main_text = text

            # 🔹 Separar anexos do corpo principal
            if annex_match:
                annex_start = annex_match.start()
                annex_text = text[annex_start:].strip()
                main_text = text[:annex_start].strip()

            # 🔹 Extrair cláusulas do corpo principal
            clause_matches = list(self.CLAUSE_REGEX.finditer(main_text))

            # ======================
            # HEADER
            # ======================
            if clause_matches:
                first_clause_start = clause_matches[0].start()
                header_text = main_text[:first_clause_start].strip()

                if header_text:
                    output_nodes.append(
                        TextNode(
                            text=header_text,
                            metadata={
                                **node.metadata,
                                "section": "header"
                            }
                        )
                    )
            else:
                # se não houver cláusula, tudo vira header
                output_nodes.append(
                    TextNode(
                        text=main_text,
                        metadata={
                            **node.metadata,
                            "section": "header"
                        }
                    )
                )

            # ======================
            # CLAUSES
            # ======================
            for match in clause_matches:
                clause_text = match.group(0).strip()
                metadata = dict(node.metadata)
                metadata["section"] = "clause"

                number_match = re.search(
                    r"CLÁUSULA\s+([A-ZÁÉÍÓÚÇ]+)",
                    clause_text,
                    re.IGNORECASE
                )

                title_match = re.search(
                    r"CLÁUSULA\s+[A-ZÁÉÍÓÚÇ]+\s*-\s*(.+)",
                    clause_text.splitlines()[0],
                    re.IGNORECASE
                )

                if number_match:
                    metadata["clause_number"] = number_match.group(1)

                if title_match:
                    metadata["clause_title"] = title_match.group(1).strip()

                output_nodes.append(
                    TextNode(
                        text=clause_text,
                        metadata=metadata
                    )
                )

            # ======================
            # ANNEXES
            # ======================
            if annex_text:
                output_nodes.append(
                    TextNode(
                        text=annex_text,
                        metadata={
                            **node.metadata,
                            "section": "annex"
                        }
                    )
                )

        return output_nodes