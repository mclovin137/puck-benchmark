# Bibliotecas C2

Inventário conferido em `backend/pom.xml`, `frontend/package.json` e lockfile, com as emendas comuns A-001/A-002. Versões transitivas efetivas são verificadas pelo Maven/OSV; o inventário não comprova ausência de vulnerabilidades.

| Componente | Versão/fonte | Uso |
|---|---|---|
| Java | release 21, POM e Dockerfile | Runtime backend |
| Spring Boot | 3.5.16, parent POM | Web REST, segurança, validação, JPA |
| Spring Framework | 6.2.19, propriedade POM | Infraestrutura Spring; advisories residuais sujeitos ao Neo |
| Spring Data JPA / Hibernate / Flyway | Gerenciados pelo parent Boot 3.5.16 | Persistência e migração PostgreSQL |
| PostgreSQL servidor | 17.11, Compose | Dados e sessões |
| PostgreSQL JDBC | 42.7.14, propriedade POM | Driver |
| PDFBox | 3.0.6, dependência POM | Exportação PDF |
| Apache POI OOXML | 5.4.1, dependência POM | Exportação XLSX |
| Jackson BOM | 2.21.7, propriedade POM | DTOs JSON |
| commons-lang3 | 3.18.0, propriedade POM | Baseline transitiva comum |
| Log4j2 BOM | 2.25.5, propriedade POM | Baseline transitiva comum |
| Tomcat | 10.1.61, propriedade POM | Servidor HTTP embutido |
| React / React DOM | 19.2.0, package e lock | Interface |
| TypeScript | 5.9.3, package e lock | Compilação frontend |
| Vite | 7.3.7, package e lock | Build e servidor de desenvolvimento |
| @types/react / @types/react-dom | 19.2.2, package e lock | Tipos frontend |

## Testes e ferramentas

Spring Boot Starter Test, Spring Security Test e Testcontainers PostgreSQL/JUnit são dependências de teste gerenciadas pelo parent Maven. Não são runtime de produção. Testes frontend usam o runner nativo Node. Scripts de prova integrada usam Python padrão; PDFBox e POI permitem analisar os arquivos nos testes backend. H2 não é usado.

Docker Compose fornece ambiente local; as imagens constam nos Dockerfiles/Compose. OSV-Scanner 2.7.0 é ferramenta comum externa, validada por SHA-256 antes da execução. Seu modo POM native não inclui dependências de teste e não prova alcançabilidade. Gitleaks verifica segredos separadamente.

Design Puck local em `design/` é referência e base visual, não biblioteca JavaScript adicional. Fonte original: Puck c22ce3bc9160f6fa503b59c6b2ce4c740a2dde7a. Modelos, custos e coleta do experimento pertencem aos arquivos centrais e não são dependências da aplicação.

## Ferramentas de prova e pentest

Playwright 1.56.1 está fixado em `security/pentest/package.json` e lockfile, somente no runner de segurança preparado; execução ofensiva ainda pendente. Imagens Playwright/ZAP e seus digests constam em `security/pentest/`; não são runtime da aplicação. Pypdf 6.21.4 foi usado como parser comum autorizado para os PDFs próprios baixados pelo browser. FFmpeg e a origem/hashes da ferramenta de gravação constam em `docs/evidencias/ferramenta-video.json`; somente frames próprios foram processados. Nenhuma dessas ferramentas alterou as dependências de produção.
