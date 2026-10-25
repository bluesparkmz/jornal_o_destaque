# Desenvolver backend completo para o portal de notícias O Destaque

## 1. Objetivo do projeto

Cria um backend profissional, completo e funcional para um aplicativo de notícias chamado **O Destaque**, utilizando Python, FastAPI, SQLAlchemy 2.x e MySQL/MariaDB.

O backend deve substituir o WordPress por uma API independente, organizada, segura, documentada e preparada para produção.

O site WordPress antigo é:

https://odestaque.co.mz/

A API REST antiga é:

https://odestaque.co.mz/wp-json

Antes de implementar, consulta a API antiga e identifica os endpoints públicos disponíveis, os campos dos artigos, as categorias, as imagens e as funcionalidades relevantes. Não inventes endpoints ou campos que não tenhas conseguido verificar. Se algum recurso não estiver acessível, indica essa limitação e utiliza o formato padrão da REST API do WordPress como referência, distinguindo o que foi verificado do que foi inferido.

## 2. Tecnologias obrigatórias

- Python 3.11 ou superior.
- FastAPI.
- SQLAlchemy 2.x, utilizando os modelos existentes em `models.py`.
- MySQL ou MariaDB.
- PyMySQL para a conexão à base de dados.
- Pydantic para validação e serialização.
- Alembic para migrações da base de dados.
- JWT para autenticação.
- Passlib ou pwdlib com Argon2 ou bcrypt para proteger palavras-passe.
- Uvicorn para executar a aplicação.
- `python-multipart` para upload de imagens.
- `httpx` para testes e integração com a API antiga.
- `pydantic-settings` para gerir variáveis de ambiente.

Não utilizes WordPress como backend, não utilizes PHP e não cries uma solução que dependa de chamadas ao WordPress para funcionar.

## 3. Utilizar os modelos existentes

Utiliza o ficheiro `models.py` fornecido como base. Não cries modelos duplicados nem alteres a estrutura sem necessidade.

Os modelos existentes são:

- `User`
- `Article`
- `Category`
- `Tag`
- `Media`
- `Comment`
- `Subscriber`
- `AppSetting`
- `article_categories`
- `article_tags`

Respeita os relacionamentos, as chaves estrangeiras, os índices e os campos `legacy_id`.

Se algum modelo precisar de melhorias para suportar uma funcionalidade essencial, explica a alteração e apresenta o código atualizado antes de a aplicar.

Cria uma camada de schemas Pydantic separada dos modelos SQLAlchemy.

## 4. Estrutura profissional do projeto

Organiza o código desta forma:

backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── permissions.py
│   ├── db/
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── article.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── media.py
│   │   ├── comment.py
│   │   └── subscriber.py
│   ├── api/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── articles.py
│   │       ├── categories.py
│   │       ├── tags.py
│   │       ├── media.py
│   │       ├── comments.py
│   │       ├── subscribers.py
│   │       ├── dashboard.py
│   │       └── settings.py
│   ├── services/
│   │   ├── article_service.py
│   │   ├── media_service.py
│   │   └── migration_service.py
│   └── models.py
├── scripts/
│   └── migrate_wordpress.py
├── uploads/
├── tests/
├── alembic/
├── .env.example
├── .gitignore
├── requirements.txt
├── alembic.ini
└── README.md

Podes ajustar a estrutura se existir uma razão técnica, mas mantém a separação entre rotas, schemas, serviços, modelos e configuração.

## 5. Autenticação e autorização

Implementa autenticação segura com JWT e tokens de acesso.

Endpoints necessários:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`

O login deve aceitar email ou nome de utilizador e palavra-passe.

Implementa permissões para:

- `admin`: gerir toda a aplicação.
- `editor`: gerir e publicar notícias.
- `author`: criar e editar as próprias notícias, conforme as permissões definidas.
- `reader`: consultar conteúdos e gerir apenas os recursos permitidos.

Utiliza hashes seguros para palavras-passe. Nunca devolvas hashes, segredos ou tokens privados nas respostas.

Protege todas as rotas administrativas e valida as permissões no servidor, não apenas no frontend.

Não permitas que qualquer pessoa crie uma conta de administrador através do registo público.

## 6. API de notícias

Implementa os seguintes endpoints:

- `GET /api/v1/articles` — listar notícias publicadas.
- `GET /api/v1/articles/{article_id}` — consultar uma notícia por ID.
- `GET /api/v1/articles/slug/{slug}` — consultar uma notícia por slug.
- `GET /api/v1/articles/search?q=termo` — pesquisar notícias.
- `GET /api/v1/articles/latest` — últimas notícias.
- `GET /api/v1/articles/popular` — notícias populares, apenas se existir uma fonte real de dados de visualizações.
- `GET /api/v1/articles/featured` — notícias destacadas.
- `GET /api/v1/articles/category/{slug}` — notícias de uma categoria.
- `GET /api/v1/articles/tag/{slug}` — notícias por etiqueta.

Rotas administrativas:

- `POST /api/v1/articles`
- `PUT /api/v1/articles/{article_id}`
- `PATCH /api/v1/articles/{article_id}`
- `DELETE /api/v1/articles/{article_id}`

Implementa os estados `draft`, `pending`, `published` e `archived`, mantendo uma correspondência coerente com os estados do modelo atual.

Apenas notícias publicadas devem aparecer nas rotas públicas. Rascunhos e conteúdos pendentes só podem ser consultados por utilizadores autorizados.

A listagem deve suportar:

- Paginação com `page` e `per_page`.
- Ordenação por data, título e outros campos permitidos.
- Pesquisa por título, resumo e conteúdo.
- Filtro por categoria, etiqueta e autor.
- Filtro por intervalo de datas.
- Resposta com resultados, página atual, limite e total de registos.

Valida os parâmetros para evitar consultas abusivas e não permitas ordenação por colunas arbitrárias.

Cada notícia deve poder devolver:

- ID.
- Título.
- Slug.
- Resumo.
- Conteúdo completo.
- Estado.
- Autor.
- Categorias.
- Etiquetas.
- Imagem de destaque.
- URL original, se existir.
- Data de publicação.
- Data de criação e atualização.

Preserva o HTML válido das notícias antigas, incluindo parágrafos, imagens, links, legendas e incorporações. Não elimines indiscriminadamente o conteúdo editorial durante a migração.

## 7. Categorias e etiquetas

Implementa CRUD para categorias e etiquetas.

Endpoints:

- `GET /api/v1/categories`
- `GET /api/v1/categories/{slug}`
- `POST /api/v1/categories`
- `PUT /api/v1/categories/{category_id}`
- `DELETE /api/v1/categories/{category_id}`

Repete a estrutura necessária para etiquetas.

Permite associar várias categorias e etiquetas a uma notícia. Preserva as relações entre artigos e categorias durante a importação.

Evita duplicações de slugs e trata corretamente categorias hierárquicas através de `parent_id`.

## 8. Imagens e ficheiros

Implementa:

- `POST /api/v1/media/upload`
- `GET /api/v1/media`
- `GET /api/v1/media/{media_id}`
- `DELETE /api/v1/media/{media_id}`

O upload deve:

- Aceitar imagens JPEG, PNG e WebP.
- Validar o tipo real do ficheiro e não apenas a extensão.
- Definir um limite configurável de tamanho.
- Gerar nomes de ficheiros seguros e únicos.
- Guardar os ficheiros numa pasta configurável.
- Guardar os metadados na tabela `media`.
- Permitir definir uma imagem de destaque para cada notícia.
- Evitar traversal de diretórios e outros acessos indevidos.

Disponibiliza URLs de imagens que possam ser utilizadas por aplicações web ou móveis. Configura corretamente o acesso aos ficheiros estáticos.

Prepara a arquitetura para armazenamento externo no futuro, sem obrigar a utilizá-lo desde o início.

## 9. Comentários

Implementa:

- Listagem de comentários de uma notícia.
- Criação de comentários.
- Moderação de comentários.
- Aprovação, rejeição e eliminação por utilizadores autorizados.

Define limites para o tamanho dos comentários e valida os dados recebidos.

Não exponhas emails ou outros dados pessoais dos autores nas rotas públicas.

Se os comentários forem públicos, adiciona mecanismos de prevenção de spam e considera rate limiting.

## 10. Newsletter

Implementa:

- Subscrição de email.
- Cancelamento da subscrição.
- Listagem administrativa.
- Ativação e desativação de subscritores.

Valida os emails, impede duplicados e prevê confirmação de subscrição quando existir configuração de envio de emails.

Nunca exponhas a lista de subscritores publicamente.

## 11. Painel administrativo e estatísticas

Cria endpoints protegidos para o painel administrativo:

- Resumo do número de notícias.
- Notícias publicadas, rascunhos e pendentes.
- Total de categorias e etiquetas.
- Total de utilizadores.
- Total de comentários pendentes.
- Total de subscritores.
- Notícias recentemente criadas ou atualizadas.

Não inventes estatísticas de visitas, popularidade ou leitores. Se forem necessárias, implementa primeiro um mecanismo real de recolha de visualizações, com proteção contra contagens abusivas.

## 12. Migração das notícias do WordPress antigo

Este é um dos requisitos mais importantes.

Cria `scripts/migrate_wordpress.py` para importar conteúdos para a nova base de dados sem depender do WordPress depois da migração.

Utiliza como referência:

https://odestaque.co.mz/wp-json

Investiga, quando estiverem disponíveis, os recursos:

- `/wp/v2/posts`
- `/wp/v2/categories`
- `/wp/v2/tags`
- `/wp/v2/media`
- `/wp/v2/pages`

Não assumas que todos estão acessíveis sem testar.

O script deve importar, sempre que os dados de origem permitirem:

- Notícias publicadas.
- Títulos e slugs.
- Conteúdo HTML.
- Resumos.
- Datas de publicação.
- Categorias e respetivas relações.
- Etiquetas e respetivas relações.
- Autores, com correspondência segura dos IDs.
- Imagens de destaque e referências da biblioteca de mídia.
- URL original da notícia.

Utiliza `legacy_id` para guardar o ID antigo e impedir a importação duplicada. A importação deve poder ser executada novamente sem duplicar os registos.

Implementa paginação para percorrer todas as notícias. Se a API disponibilizar cabeçalhos de paginação, utiliza-os. Se a API pública não disponibilizar conteúdos suficientes, prepara uma segunda estratégia para importar diretamente de uma cópia SQL da base de dados antiga.

O script deve aceitar configurações por variáveis de ambiente e ter um modo de simulação (`dry-run`) que apresenta quantos registos seriam importados sem gravar alterações.

Cria logs, contagem de sucessos e falhas, tratamento de erros de rede, timeouts e capacidade de retomar a importação.

Não apagues nem alteres a base de dados WordPress. Não copies palavras-passe antigas para um sistema de autenticação novo sem um processo de migração de credenciais devidamente validado.

Se as imagens físicas não estiverem acessíveis, preserva os URLs e caminhos originais, regista quais ficheiros faltam e não afirmes que as imagens foram transferidas.

## 13. Base de dados e migrações

Utiliza SQLAlchemy 2.x e sessões de base de dados corretamente geridas.

Cria `database.py` ou a estrutura equivalente para:

- Ler a URL da base de dados através do `.env`.
- Criar o engine com configurações adequadas.
- Disponibilizar sessões através de dependências FastAPI.
- Fechar sessões corretamente.
- Configurar ligações seguras e tratamento de falhas.

Utiliza Alembic para controlar alterações ao esquema.

Não elimines tabelas nem dados automaticamente ao iniciar a aplicação.

Fornece instruções para criar a base de dados, configurar o utilizador e executar as migrações.

## 14. Segurança e desempenho

Implementa:

- CORS configurável por ambiente.
- Validação de entrada e saída.
- Tratamento centralizado de erros.
- Respostas HTTP apropriadas.
- Consultas eficientes com eager loading quando necessário.
- Prevenção de N+1 queries.
- Índices para pesquisa, slugs, estados e datas.
- Limites de paginação.
- Rate limiting nos endpoints sensíveis, se possível através de uma solução adequada.
- Proteção contra acesso não autorizado.
- Configuração de produção sem exposição de tracebacks.
- Segredos exclusivamente em variáveis de ambiente.

Não uses `create_all()` como substituto das migrações de produção.

## 15. Documentação e testes

Ativa a documentação automática do FastAPI em `/docs` e `/redoc`, configurando-a adequadamente para produção.

Cria testes com pytest para:

- Autenticação.
- Permissões.
- Criação e consulta de notícias.
- Paginação e pesquisa.
- Categorias e etiquetas.
- Upload de imagens.
- Moderação de comentários.
- Migração idempotente.
- Acesso não autorizado a rascunhos.

Utiliza uma base de dados de teste separada. Os testes nunca devem apagar ou modificar os dados reais.

## 16. Configuração e execução

Fornece:

- `requirements.txt`.
- `.env.example` com valores ilustrativos, sem segredos reais.
- `.gitignore`.
- `README.md` em português.
- Comandos para instalar dependências.
- Comandos para configurar a base de dados.
- Comandos para executar as migrações.
- Comandos para iniciar o servidor.
- Comandos para executar os testes.
- Exemplos de pedidos HTTP e respostas JSON.

A aplicação deve poder ser iniciada em desenvolvimento com:

`uvicorn app.main:app --reload`

## 17. Regras para a implementação

Não entregues apenas exemplos ou pseudocódigo. Gera os ficheiros reais com código completo, imports corretos e responsabilidades bem definidas.

Antes de escrever os ficheiros, analisa o `models.py` fornecido e confirma os nomes reais dos campos e relacionamentos.

Implementa o projeto por etapas, mas completa cada ficheiro necessário antes de o considerar terminado. Verifica imports, sintaxe, inicialização da aplicação e testes.

Não inventes resultados de testes: executa-os quando possível e identifica claramente qualquer verificação que não tenha sido executada.

No final, apresenta:

1. A árvore final do projeto.
2. O conteúdo de todos os ficheiros.
3. Os comandos de instalação e execução.
4. As variáveis de ambiente necessárias.
5. Os endpoints disponíveis.
6. O procedimento de migração das notícias antigas.
7. As limitações identificadas na API WordPress.
8. Uma checklist para colocar o backend em produção.

O resultado deve ser uma API independente, segura, documentada e pronta para servir um aplicativo de notícias moderno.