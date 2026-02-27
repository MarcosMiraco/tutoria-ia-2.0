

# Chat Seguros Agent

Este projeto é um agente de consulta para documentos de Convenções Coletivas de Trabalho (CCTs), utilizando RAG (Retrieval-Augmented Generation) para responder perguntas sobre direitos, obrigações e cláusulas.

## Instalação e Execução

O projeto utiliza o Poetry para gerenciamento de dependências e execução.

### 1. Instale o Poetry

Se ainda não possui o Poetry instalado, execute:

```bash
pip install poetry
```

Mais informações: https://python-poetry.org/docs/#installation

### 2. Instale as dependências do projeto

```bash
poetry install
```

### 3. Execute o servidor localmente

```bash
poetry run python ./src/main.py
```

O servidor será iniciado em:

```
http://127.0.0.1:5000
```

## Requisito: Serviço RAG

Para funcionamento correto, é necessário que o serviço RAG esteja rodando e acessível localmente (por padrão em http://127.0.0.1:8000/query).

## Endpoint: /ask

O endpoint `/ask` aceita requisições POST para realizar perguntas sobre documentos.

### Exemplo de payload aceito:

```json
{
	"question": "Minha Pergunta Aqui",
}
```

### Resposta esperada:

```json
{
	"response": "resposta da ia",
    "status": "success"
}
```

## Observações

- O endpoint `/ask` está disponível em http://127.0.0.1:5000/ask
- O serviço depende do RAG estar disponível em http://127.0.0.1:8000/query
- O frontend pode acessar o backend se estiver rodando em http://localhost:5173 (CORS habilitado)

## Documentação Swagger (OpenAPI)

Após iniciar o servidor, acesse a interface interativa do Swagger em:

```
http://127.0.0.1:5000/docs
```

Você pode testar os endpoints diretamente pela interface web.