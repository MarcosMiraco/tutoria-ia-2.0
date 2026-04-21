from client.http import rag_service_query

def llm_rag_tool(query: str, top_k: int = 8, filters: dict = None) -> str:
    # --------------------------------------- ORIGINAL --------------------------------------------------------
    # """
    # Utilize quando precisar de Consulta RAG sobre documentos de Convenções Coletivas de Trabalho (CCTs),
    # que contêm informações legais definindo direitos, deveres e condições de trabalho para categorias profissionais específicas,
    # entre sindicatos de trabalhadores e empregadores.

    # Parâmetros de uso:

    # 1. **query (str)**: texto da consulta ou pergunta do usuário.
    #    - Descreve o que você quer saber sobre direitos, obrigações ou cláusulas da CCT.
    #    - Exemplo: "Empresas do setor varejista precisam oferecer assistência médica obrigatória?"

    # 2. **top_k (int, opcional)**: número máximo de resultados relevantes a serem retornados.
    #    - Para perguntas mais gerais opt entre 8 e 20
    #    - Permite limitar a quantidade de documentos ou trechos retornados pelo RAG.
    #    - Exemplo: `top_k = 5` retornará até os 5 trechos mais relevantes.

    # 3. **filters (dict, opcional)**: permite restringir a busca utilizando metadados da CCT.  
    #    Cada chave representa um metadado disponível e deve ser usada com seu valor correspondente.
    #    - **file_name**: nome do arquivo da CCT.
    #        - Ex.: `"ICRegistrado30964546.doc"`
    #    - **registro_mte**: número de registro oficial no Ministério do Trabalho.
    #        - Ex.: `"SP000154/2026"`
    #    - **data_registro_mte**: data de registro no MTE. Formato: DD/MM/AAAA.
    #        - Ex.: `"06/01/2026"`
    #    - **solicitacao**: número de solicitação do sindicato ou interno.
    #        - Ex.: `"MR061798/2025"`
    #    - **processo**: número de processo administrativo ou judicial relacionado.
    #        - Ex.: `"47979.265784/2025-92"`
    #    - **data_protocolo**: data de protocolo da solicitação ou registro. Formato: DD/MM/AAAA.
    #        - Ex.: `"03/11/2025"`
    #    - **segment**: setor ou segmento econômico da CCT (saúde, varejo, indústria, educação, hotelaria, etc.).
    #        - Ex.: `"saúde"`
    #    - **section**: seção do documento para filtragem mais granular (cláusula, capítulo, artigo).
    #        - Ex.: `"clause"`
    #    - **clause_number**: número ou identificador da cláusula específica.
    #        - Ex.: `"QUARTA"`

    #    - **clause_title**: título ou resumo da cláusula.
    #        - Ex.: `"REAJUSTE SALARIAL"`

    # Exemplo completo de chamada ao RAG:

    #     query = "Esse sindicato obriga seguro de vida empresarial?"
    #     top_k = 5
    #     filters = {
    #         "segment": "saúde",
    #         "section": "clause",
    #         "clause_number": "QUARTA",
    #         "clause_title": "REAJUSTE SALARIAL"
    #     }

    # A resposta deve retornar documentos relevantes no formato:

    #     "Contexto 1:
    #     Texto: ...conteúdo do documento...
    #     Metadados: { 'file_name': 'ICRegistrado30964546.doc', 'segment': 'saúde', 'clause_number': 'QUARTA', ... }

    #     Contexto 2:
    #     Texto: ...conteúdo do documento...
    #     Metadados: { ... }
    #     "

    # Use a `query` como input principal, `top_k` para limitar resultados e `filters` para refinar a busca com metadados.
    # """
    # --------------------------------------- REFATORADA --------------------------------------------------------
    """
    Busca informações nos documentos indexados (CCTs e notas pessoais do Obsidian).
    Use esta ferramenta para responder qualquer pergunta factual ou específica do usuário.
    
    Args:
        query: pergunta ou tema a buscar
        top_k: número de resultados (padrão 5)
        filters: filtros opcionais, ex: {"file_type": "text/markdown"} para notas ou {"file_type": "doc"} para CCTs
    """
    results = rag_service_query(query, top_k, filters)
    docs = results.get("results", [])
    output = []
    for idx, item in enumerate(docs, 1):
        doc_text = item.get("doc", "")
        metadata = item.get("metadata", {})
        meta_str = "; ".join(f"{k}: {v}" for k, v in metadata.items())
        output.append(f"Contexto {idx}:\nTexto: {doc_text}\nMetadados: {meta_str}\n")
    return "\n".join(output)
