# Bibliotecas do cenário C1

Versões conferidas nos manifests e lockfile deste cenário em 2026-11-06.

## Runtime

| Componente | Versão/fonte | Finalidade |
| --- | --- | --- |
| Java | 21 (`backend/pom.xml`, imagem Temurin) | API |
| Spring Boot | 3.5.16 | REST e configuração |
| Spring Data JPA | gerenciado por Spring Boot 3.5.16 | Persistência relacional |
| Jackson BOM | 2.21.7 (override A-002) | JSON e formatos usados pelo Spring/Flyway |
| Apache Commons Lang | 3.18.0 (override A-002) | Dependência transitiva |
| Log4j2 BOM | 2.25.5 (override A-002) | Logging transitivo |
| Tomcat embed | 10.1.61 (override A-002) | Servidor HTTP embutido |
| PostgreSQL JDBC | 42.7.14 (override A-002) | Acesso PostgreSQL |
| Flyway | gerenciado por Spring Boot 3.5.16 | Migrações |
| PDFBox | 3.0.6 | Geração de PDF |
| Apache POI OOXML (`org.apache.poi:poi-ooxml`) | 5.4.1 | Geração XLSX |
| React / React DOM | 19.2.0 | Interface |
| TypeScript | 5.9.3 | Tipagem frontend |
| Vite | 7.3.7 | Build e desenvolvimento |

## Desenvolvimento e testes

| Componente | Versão/fonte | Finalidade |
| --- | --- | --- |
| Maven | imagem 3.9.9; compatível Maven Wrapper ausente | build/testes Java |
| JUnit/Spring Boot Test | gerenciado por Spring Boot 3.5.16 | testes Java |
| Vitest | 4.1.12 | testes frontend |
| Node | 24.16.0 | build frontend |
| Nginx | 1.29.3-alpine (`frontend/Dockerfile`) | servir frontend e encaminhar `/api` para a API |
| Docker Compose | `compose.yaml` | execução local |

A versão Vitest 3.2.4 apresentou achados válidos em GHSA-5gmw-xhrv-c9v3, GHSA-85c8-ppgw-ccpr, GHSA-82fw-gwwq-j7x9, GHSA-qxg6-89mg-rqv8 e GHSA-5xrq-8626-4rwp; foi atualizada para 4.1.12. A auditoria npm final não reportou vulnerabilidades. A atualização atravessou a major do runner de testes e não altera runtime de produção.

As dependências transitivas são fixadas pelo `frontend/package-lock.json` e pela árvore Maven gerenciada pelo parent Spring Boot. A baseline de segurança A-001 atualizou Spring Boot para 3.5.16, Vite para 7.3.7 e PostgreSQL para 17.11 para todos os cenários. A-001 ocorreu durante a implementação C1; o ajuste é intervenção comum registrada pelo experimento.


**Risco aberto:** a evidência pré-A-002 registrou 23 findings Java. A varredura C1 pós-A-002 (`evidences/osv-java-a002-summary.json`) extraiu 10 pacotes e deixou 2 advisories Spring WebMVC 6.2.19; 7 pacotes foram filtrados como não escaneáveis. Ambos permanecem abertos para triagem Neo; Dependency-Check Java está bloqueado sem a configuração NVD. Segurança não está aprovada.

### Emenda comum A-002

A-002 fixa Jackson BOM 2.21.7, commons-lang3 3.18.0, Log4j2 BOM 2.25.5, Tomcat 10.1.61 e PostgreSQL JDBC 42.7.14, mantendo Spring Boot 3.5.16 e Spring Framework 6.2.19. A árvore Maven C1 foi verificada em 2026-11-06 por `mvn dependency:tree`; esses pins são intervenção comum de baseline e o retrabalho correspondente fica registrado pelo Oráculo.
