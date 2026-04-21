## Exercício: Novo Fluxo RAG com Dataset Diferente

1. **Escolha um novo dataset** de documentos (ex: artigos científicos, notícias, manuais técnicos, etc.).
2. **Crie um novo módulo de loader** para importar e estruturar os dados desse dataset.
3. **Implemente um módulo de transformação de documentos**, adaptando o conteúdo para o formato utilizado no pipeline RAG.
4. **Desenvolva um chunker personalizado** para dividir os documentos em partes relevantes para o fluxo de recuperação.
5. **Teste o novo fluxo RAG** utilizando esses módulos, verificando a performance e a qualidade das respostas geradas.

**Documente cada etapa**, explique as decisões tomadas e compare os resultados com o fluxo original.


# Introdução

Na escolha de dataset eu queria resolver um problema real e pessoal. Pensando nisso resolvi por adicionar o suporte a arquivos "md", eu uso obsidian como principal programa de escrever notas, não parei para contar tudo que eu tenho, mas fazendo uma contagem de cabeça devo ter 600+ notas, eu sou bem organizado então tenho notas de index para achar notas, mas eu queria integrar isso no RAG, eu mesmo tenho um assistente feito em .NET + ollama em que eu queria essa capacidade de dar upload de arquivos e consultados no meu assistente, esse projeto foi muito bom para mim aprender como se faz isso.

# Maiores Desafios

Comecei tentando escrever o transformer, tentei fazer um MarkdownDocumentParser, mas acabei me atrapalhando muito, não sabia bem quais eram os retornos de cada chamada e o que cada metodo estava recebendo. Partes do código como:

transformers.py
```python
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
```
chunker.py
```python
@ChunkerRegistry.register("cct")
class CctDocumentChunker:
    def get_transform(self):
        return CCTClauseParser(
            max_tokens=1800
        )
```

Estavam me deixando muito confuso. Nesse ponto parei de tentar mudar o que eu não estava entendo e me foquei em debugar o código e enteder o que cada pedaço estava fazendo e como tudo se misturava. Eu tentei fazer uma chave da openai. Bom, fazer a chave foi fácil, mas ao integrar a chave no .env onde era relevante não estava funcionando de forma alguma. Eu fiquei por um tempo vergonhoso tentando fazer funcionar até que veio na minha cabeça que o problema era o limite, não estava funcionando por que eu não tinha limite de uso para nenhum modelo. Não sei como já que eu não tinha usado a api do openai nenhuma vez mas a minha cota de uso esatava em $0.00. Já que eu não queria pagar para fazer a tarefa eu resolvi por trocar da openai para usar o ollama localmente na qual já estou familiarizado. Aqui foi onde eu acabei perdendo mais tempo, depois que troquei para ollama ficou mais fácil de eu prosseguir.

# Conclusão

Depois que eu consegui trocar para modelos ollama ficou mais fácil. Deu para eu debugar tudo localmente, entender o que cada metodo recebia e comecei a fazer as minhas próprias implementações. Comecei fazendo um loader que pega de uma pasta somente os arquivos md:

```python
@LoaderRegistry.register("md")
class MarkdownLoader:
    def load(self, source: str):
        loader = SimpleDirectoryReader(
            input_dir=source,
            encoding="UTF-8",
            required_exts=[".md"],
            recursive=True
        )

        return loader.load_data()
```

Fiz isso por que eu não queria misturar os meus contextos dos arquivos do meu obsidian com os arquivos doc de cct. Usei UTF-8 pois foi o encoding que ficou sem nenhum caractere quebrado.
Depois parti para o chunker:

```python
class MarkdownDocumentParser(NodeParser):
    fallback_chunk_size: int = 512
    fallback_overlap: int = 50

    @property
    def fallback_splitter(self):
        return SentenceSplitter(
            chunk_size=self.fallback_chunk_size
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
            top_level = self._detect_top_level(text)  
            if top_level is None:
                chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
            else:
                chunks = self._split_by_heading(text, top_level)

            for i, chunk in enumerate(chunks):
                output_nodes.append(
                    TextNode(
                        text=chunk,
                        metadata={**node.metadata, "chunk_index": i}
                    )
                )
        return output_nodes

  

    @staticmethod
    def _detect_top_level(text: str) -> int | None:
        """Retorna o menor nível de heading encontrado (1, 2, 3...) ou None."""
        for level in range(1, 7):
            pattern = re.compile(rf"^{'#' * level} .+", re.MULTILINE)
            if pattern.search(text):
                return level
        return None

    @staticmethod
    def _split_by_heading(text: str, level: int) -> List[str]:
        """Divide o texto nas ocorrências do heading do nível especificado."""
        pattern = re.compile(rf"(?=^{'#' * level} )", re.MULTILINE)
        parts = pattern.split(text)
        return [p.strip() for p in parts if p.strip()]
```

A primeira versão que eu fiz foi bem mais simples é claro, primeiro eu tinha só esse split por "\n\n" mas depois eu fiz essa lógica de separar pelos titulos, tem essa lógica de pegar o primeiro nível de título por que eu tento manter um padrão mas nos meus arquivos pessoais tem alguns que o nível mais alto é "#", outros que é "##" e etc. Então precisava de um filtro que suportasse vários níveis. 
Quando comecei a dar ingest nos arquivos eu tive um problema "{ detail : <MilvusException: (code=65535, message=the length(3840) of float data should divide the dim(3072))> }", eu descobri que isso estava acontecendo aqui:

```python
async def get_vector_store():
    global vector_store
    if vector_store is None:
        async with _init_lock:
            if vector_store is None:
                vector_store = VectorStoreFactory.create(
                    "milvus",
                    collection_name="cct_docs",
                    # dim=3072,
                    dim=768,
                    uri="http://localhost:19530",
                    metric_type="COSINE",
                    M=32,
                    ef_construction=300
                )
    return vector_store
```

o problema era o parametro "dim" que estava em 3072 dimensões, como eu troquei a llm o embedding mudou e o banco de dados não estava mais aceitando, depois que mudei para 768 deu tudo certo.
A penúltima mudança que fiz foi no transformers:

```python
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
                if skip_block and line.startswith("  "):
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
        return re.sub(r"<span[^>]*>(.*?)</span>", r"\1", text
```

Já que no meu obsidian utilizo callouts que seguem a sintaxe de ">[!...]" e também útilizo a propriedade "cssclasses" eu queria limpar esses valores para que a resposta final do RAG ficasse melhor e mais limpa, já que essas partes da nota não mudam em nada o conteúdo em si.
Como última mudança eu diminui os prompts do projeto, pois com os modelos com menor capacidade a alta quantidade de informações estava os deixando confusos e as respostas não estava muito boas, algumas vezes o modelo não estava nem fazendo uso da tool, outras estava usando 2-3 vezes, diminuindo as prompts melhorou bastante o tempo/qualidade das respostas.

Aqui um exemplo de resposta que foi obtida em 1m 9s:

Pergunta:
```json
{
  "question": "Qual a minha rotina de treino?"
}
```

Resposta:
```json
{
  "response": "Com base nos documentos consultados, aqui está a rotina de treino que você mencionou:\n\n- Apoio  x10\n- Agachamento x20\n- Prancha com perna x20\n- Passada x20\n- Abdominal x10\n- Flexão x5\n- 1 minuto de prancha sem perna\n\nEssa rotina parece focar em uma combinação de força, resistência e flexibilidade. Se você tiver mais perguntas sobre treino ou precisar de ajuda com algo específico, estou aqui para ajudar!",
  "status": "success"
}
```