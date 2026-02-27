from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator, FilterCondition
from typing import Dict, Any

class MetadataFilterFactory:
    """
    Constrói MetadataFilters do LlamaIndex a partir de um dict simples.
    """

    @staticmethod
    def from_dict(filter_dict: Dict[str, Any], condition: FilterCondition = FilterCondition.AND) -> MetadataFilters | None:
        """
        Converte um dict {'segment': 'saúde'} em MetadataFilters
        """
        if not filter_dict:
            return None

        filters = [
            MetadataFilter(
                key=key,
                value=value,
                operator=FilterOperator.EQ  # por padrão usamos igualdade
            )
            for key, value in filter_dict.items()
        ]

        return MetadataFilters(filters=filters, condition=condition)