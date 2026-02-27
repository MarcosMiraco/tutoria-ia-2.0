## Serviço RAG para Indexação de CCT e Query Retrieval
> **Importante:** Para o funcionamento do servidor de armazenamento vetorial (Milvus), é necessário subir os containers definidos no arquivo `docker-compose.yml` antes de iniciar a aplicação:

```
docker-compose up -d
```

Esse passo garante que o serviço de vectorstore estará disponível para indexação e recuperação.

Este sistema é um serviço RAG (Retrieval-Augmented Generation) desenvolvido para indexação de CCT e recuperação de documentos relevantes. Ele é essencial para o funcionamento do Agente de IA, fornecendo uma base robusta para consultas e respostas inteligentes.

### Gerenciamento de Dependências
O projeto utiliza o [Poetry](https://python-poetry.org/) para gerenciamento de dependências e ambiente.

#### Instalação do Poetry
Para instalar o Poetry, execute o comando abaixo:

```
pip install poetry
```
Ou siga as instruções oficiais em [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

### Como rodar a aplicação
Após instalar as dependências com Poetry, execute:

```
poetry install
poetry run python ./src/main.py
```

### Acessando a documentação Swagger
Após iniciar a aplicação, acesse a documentação interativa (Swagger UI) pelo navegador:

```
http://localhost:8000/docs
```

Essa interface permite testar os endpoints e visualizar os modelos de requisição e resposta.

### Relação com o Agente de IA
Este serviço é necessário para o funcionamento do Agente de IA, pois realiza a indexação e recuperação de informações técnicas, permitindo respostas precisas e contextualizadas.

---

## Documentação dos Endpoints

### 1. Consulta de documentos
**POST /query**

Recebe uma query e retorna os documentos mais relevantes.

**Payload de exemplo:**
```json
{
	"query": "minha pergunta?",
	"top_k": 5,
	"filters": {
        "sergment": "varejo",
        "file_name": "ICRegistrado19522063.doc"
    }
}
```

**Resposta:**
```json
{
	"results": [
		{"text": "doc1", "metadata": "..."},
		{"text": "doc2", "metadata": "..."}
	]
}
```

---

### 2. Indexação de documentos
**POST /docs/ingest**

Recebe informações sobre o tipo de loader, chunker, fonte e pipeline de transformação para indexar novos documentos.

**Payload de exemplo:**
```json
{
  "loader_type": "dir",
  "source": "./src/assets",
  "chunker_type": "cct",
  "transform_pipeline": [
    "html-sanitizer",
    "normalize",
    "mte-header",
    "llm-category-extractor"
  ]
}
```

**Resposta:**
```json
{
	"status": "success"
}
```

---

### 3. Reset do vectorstore
**DELETE /vs/reset**

Remove todos os dados do vectorstore/Collections (apenas para uso em desenvolvimento).

**Resposta:**
```json
{
	"result": "Vectorstore resetado com sucesso"
}
```
