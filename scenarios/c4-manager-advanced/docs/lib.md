# Bibliotecas e ferramentas C4
Fonte: backend/pom.xml e frontend/package-lock.json; baseline efetiva A001/A002. Sem bibliotecas compartilhadas de outros cenários.

| Componente | Versão | Finalidade |
|---|---|---|
| Java | release21 | backend (host de autoria25; containers21) |
| Spring Boot |3.5.16| REST, Security, JPA, Validation, testes |
| Spring Framework |6.2.19 via Boot| REST;2advisories A002 ainda no componente, parecer Neo pendente |
| Jackson BOM |2.21.7| DTO/JSON |
| Tomcat |10.1.61| HTTP |
| PostgreSQL servidor/JDBC |17.11 /42.7.14| banco/driver |
| Flyway |11.7.2 via Boot| migração V1 |
| PDFBox |3.0.6| PDF com fonte DejaVuSans embutida/licença em resources/fonts |
| POI OOXML |5.4.1| XLSX, valores monetários textuais para precisão |
| Commons Lang3 |3.18.0| override transitivo de segurança A002 |
| Log4j2 BOM |2.25.5| override A002 |
| React / ReactDOM |19.2.0| UI |
| TypeScript |5.9.3| tipagem e build |
| Vite |7.3.7| build/proxy local |
| Tipos React/DOM |19.2.2| ferramentas TS |
| Vitest |4.1.12| testes unitários frontend; atualizado após OSV detectar advisories em3.2.4 |
| Playwright |1.56.1| jornadas, screenshots e gravação separada |
| axe-core/playwright |4.11.0| auditoria WCAG automática |
| Testcontainers |gerenciado por Boot| PostgreSQL real descartável em teste |
| JaCoCo |0.8.14| cobertura backend |
| CycloneDX Maven |2.9.1 (ferramenta)| SBOM resolvido |
| OSV Scanner |2.7.0 (ferramenta comum)| advisories de SBOM/lock |

O lockfile fixa transitivos do frontend; backend gera target/bom.json. Fonte Puck fixada e design são referências/governança, não dependências de runtime.
