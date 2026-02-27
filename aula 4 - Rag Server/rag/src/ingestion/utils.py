import re

FIELD_PATTERNS = {
    "registro_mte": r"NÚMERO\s+DE\s+REGISTRO\s+NO\s+MTE:\s*([\w\/\-]+)",
    "data_registro_mte": r"DATA\s+DE\s+REGISTRO\s+NO\s+MTE:\s*(\d{2}/\d{2}/\d{4})",
    "solicitacao": r"NÚMERO\s+DA\s+SOLICITAÇÃO:\s*([\w\/\-]+)",
    "processo": r"NÚMERO\s+DO\s+PROCESSO:\s*([\d\.\-\/]+)",
    "data_protocolo": r"DATA\s+DO\s+PROTOCOLO:\s*(\d{2}/\d{2}/\d{4})",
}


def extract_fields(text: str) -> dict:
    result = {}

    for key, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[key] = match.group(1)

    return result


HEADER_SECTION_PATTERN = re.compile(r"(.*?)\bCLÁUSULA\s+[A-ZÀ-ÿ0-9]+[\s-]", re.IGNORECASE | re.DOTALL)

def extract_header_content(text: str) -> str:
    """
    Retorna o header de um CCT, ou seja, todo conteúdo até a primeira cláusula.
    
    Args:
        text (str): Texto completo do CCT.
    
    Returns:
        str: Conteúdo do header, pronto para análise de segmento.
    """
    match = HEADER_SECTION_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()