# Chatbot Frontend (React + Vite)

Este projeto é um frontend de chatbot construído com React e Vite, que se comunica com uma API inteligente para responder perguntas sobre Convenções Coletivas de Trabalho e seguros empresariais.

## Pré-requisitos
- Node.js (recomendado v18 ou superior)
- npm 

## Instalação
1. Clone o repositório ou baixe o código-fonte.
2. No terminal, navegue até a pasta do projeto
3. Instale as dependências:
   ```sh
   npm install
   ```

## Rodando o projeto localmente
Execute o comando abaixo para iniciar o servidor de desenvolvimento:
```sh
npm run dev
```

O Vite irá iniciar o frontend em modo desenvolvimento. Normalmente estará disponível em [http://localhost:5173](http://localhost:5173).

## Observações
- Certifique-se de que a API backend (por exemplo, FastAPI em http://127.0.0.1:5000) esteja rodando para que o chatbot funcione corretamente.
- O chat utiliza o localStorage do navegador para armazenar as conversas.

---
