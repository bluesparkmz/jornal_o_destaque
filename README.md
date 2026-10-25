# O Destaque API

Backend FastAPI independente do WordPress. A estrutura segue a convenção do projecto: `models.py`, `schemas.py` e `main.py` na raiz; rotas em `routers/`; regras de negócio em `controllers/`.

## Arranque

1. Crie o ambiente virtual e instale `pip install -r requirements.txt`.
2. Copie `.env.example` para `.env` e defina uma senha MySQL e uma `JWT_SECRET_KEY` aleatória com 32 ou mais caracteres.
3. Crie a base de dados MariaDB/MySQL. As tabelas devem ser aplicadas por uma migração Alembic (a inicialização nunca executa `create_all`).
4. Execute `uvicorn main:app --reload` dentro desta pasta.

A documentação fica em `/docs`; a verificação de serviço em `/health`.

## Limitação de migração

A consulta pública a `https://odestaque.co.mz/wp-json` não esteve acessível durante a implementação. O dump local `olddb.sql` permanece a fonte disponível; palavras-passe WordPress não devem ser copiadas para este sistema.
