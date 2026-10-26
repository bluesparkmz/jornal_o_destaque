# O Destaque API

Backend FastAPI independente do WordPress. A estrutura segue a convenção do projecto: `models.py`, `schemas.py` e `main.py` na raiz; rotas em `routers/`; regras de negócio em `controllers/`. A base de dados é PostgreSQL.

## Arranque

1. Crie o ambiente virtual e instale `pip install -r requirements.txt`.
2. Copie `.env.example` para `.env`, defina `DATABASE_URL` com a ligação PostgreSQL e uma `JWT_SECRET_KEY` aleatória com 32 ou mais caracteres.
3. Crie a base de dados PostgreSQL. No primeiro arranque, a aplicação cria automaticamente as tabelas que ainda não existirem através de `Base.metadata.create_all()`.
4. Execute `uvicorn main:app --reload` dentro desta pasta.

A documentação fica em `/docs`; a verificação de serviço em `/health`.

## Limitação de migração

A consulta pública a `https://odestaque.co.mz/wp-json` não esteve acessível durante a implementação. O dump local `olddb.sql` permanece a fonte disponível; palavras-passe WordPress não devem ser copiadas para este sistema.
