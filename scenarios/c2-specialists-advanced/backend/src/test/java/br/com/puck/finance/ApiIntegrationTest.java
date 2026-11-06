package br.com.puck.finance;

import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.*;
import java.io.ByteArrayInputStream;
import java.util.*;
import java.util.concurrent.*;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.*;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.testcontainers.containers.PostgreSQLContainer;

@SpringBootTest
@AutoConfigureMockMvc
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ApiIntegrationTest {
  private static final String SCHEMA = "test_" + UUID.randomUUID().toString().replace("-", "");
  private static PostgreSQLContainer<?> postgres;

  @DynamicPropertySource
  static void properties(DynamicPropertyRegistry registry) {
    String url = System.getenv("TEST_DB_URL");
    if (url == null) {
      postgres = new PostgreSQLContainer<>("postgres:17.11");
      postgres.start();
      registry.add("spring.datasource.url", postgres::getJdbcUrl);
      registry.add("spring.datasource.username", postgres::getUsername);
      registry.add("spring.datasource.password", postgres::getPassword);
    } else {
      registry.add("spring.datasource.url", () -> url);
      registry.add(
          "spring.datasource.username",
          () -> System.getenv().getOrDefault("TEST_DB_USER", "finance"));
      registry.add("spring.datasource.password", () -> System.getenv("TEST_DB_PASSWORD"));
    }
    registry.add("spring.flyway.schemas", () -> SCHEMA);
    registry.add("spring.jpa.properties.hibernate.default_schema", () -> SCHEMA);
  }

  @Autowired org.springframework.context.ApplicationContext context;

  @Autowired
  org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping mappings;

  @Autowired MockMvc mvc;
  @Autowired ObjectMapper json;
  @Autowired JdbcTemplate jdbc;
  String alice, bob;
  String aliceEmail;
  String bobEmail;
  String password = "senhasegura" + "é".repeat(70) + "A";

  @BeforeAll
  void users() throws Exception {
    aliceEmail = "alice-" + UUID.randomUUID() + "@example.test";
    bobEmail = "bob-" + UUID.randomUUID() + "@example.test";
    alice = registerAndLogin(aliceEmail);
    bob = registerAndLogin(bobEmail);
  }

  String registerAndLogin(String email) throws Exception {
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", " Pessoa Ágil ", "email", email, "password", password),
        201);
    return request(post("/api/auth/login"), null, Map.of("email", email, "password", password), 200)
        .path("token")
        .asText();
  }

  JsonNode request(MockHttpServletRequestBuilder builder, String token, Object body, int status)
      throws Exception {
    if (token != null) builder.header("Authorization", "Bearer " + token);
    if (body != null) builder.contentType("application/json").content(json.writeValueAsBytes(body));
    byte[] bytes =
        mvc.perform(builder)
            .andExpect(status().is(status))
            .andReturn()
            .getResponse()
            .getContentAsByteArray();
    return bytes.length == 0 ? json.nullNode() : json.readTree(bytes);
  }

  Map<String, Object> movement(
      String description, String category, String amount, String type, String date) {
    return Map.of(
        "description",
        description,
        "category",
        category,
        "amount",
        amount,
        "type",
        type,
        "date",
        date);
  }

  JsonNode create(String token, String description, String category, String amount, String type)
      throws Exception {
    return request(
        post("/api/transactions"),
        token,
        movement(description, category, amount, type, "2026-06-15"),
        201);
  }

  byte[] file(String route, String token, String category) throws Exception {
    return mvc.perform(
            get("/api/transactions/" + route)
                .param("category", category)
                .param("size", "1")
                .header("Authorization", "Bearer " + token))
        .andExpect(status().isOk())
        .andReturn()
        .getResponse()
        .getContentAsByteArray();
  }

  @Test
  void unauthorizedResponsesUseUtf8WithMissingOrInvalidToken() throws Exception {
    for (String token : List.of("", "Bearer invalid-token")) {
      var request = get("/api/auth/me");
      if (!token.isEmpty()) request.header("Authorization", token);
      var response =
          mvc.perform(request).andExpect(status().isUnauthorized()).andReturn().getResponse();
      assertThat(response.getCharacterEncoding()).isEqualTo("UTF-8");
      assertThat(response.getContentType()).contains("application/json", "charset=UTF-8");
      assertThat(response.getContentAsByteArray())
          .isEqualTo(
              "{\"message\":\"Autenticação necessária\"}"
                  .getBytes(java.nio.charset.StandardCharsets.UTF_8));
    }
  }

  @Test
  void credentialsValidationAndRealRevocation() throws Exception {
    request(get("/api/auth/me"), null, null, 401);
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", "X", "email", aliceEmail.toUpperCase(), "password", password),
        409);
    request(
        post("/api/auth/login"),
        null,
        Map.of("email", aliceEmail, "password", password.substring(0, password.length() - 1) + "B"),
        401);
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", "X", "email", "bad", "password", "short"),
        400);
    var normalized =
        request(
                post("/api/auth/login"),
                null,
                Map.of("email", " " + aliceEmail.toUpperCase() + " ", "password", password),
                200)
            .path("token")
            .asText();
    assertThat(request(get("/api/auth/me"), normalized, null, 200).path("name").asText())
        .isEqualTo("Pessoa Ágil");
    request(post("/api/auth/logout"), normalized, null, 204);
    request(get("/api/auth/me"), normalized, null, 401);
    request(get("/api/auth/me"), alice, null, 200);
  }

  @Test
  void loginCredentialStatusAndPasswordBoundaries() throws Exception {
    request(post("/api/auth/login"), null, Map.of("email", aliceEmail, "password", "wrong"), 401);
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", "Limite", "email", "short@example.test", "password", "wrong"),
        400);
    String boundaryEmail = "boundary-" + UUID.randomUUID() + "@example.test";
    String boundaryPassword = "a".repeat(128);
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", "Limite", "email", boundaryEmail, "password", boundaryPassword),
        201);
    assertThat(
            request(
                    post("/api/auth/login"),
                    null,
                    Map.of("email", boundaryEmail, "password", boundaryPassword),
                    200)
                .path("token")
                .asText())
        .isNotBlank();
    request(
        post("/api/auth/login"),
        null,
        Map.of("email", boundaryEmail, "password", "a".repeat(129)),
        400);
    request(
        post("/api/auth/register"),
        null,
        Map.of("name", "Limite", "email", "long@example.test", "password", "a".repeat(129)),
        400);
  }

  @Test
  void expiredSessionCannotBeUsed() throws Exception {
    var token =
        request(post("/api/auth/login"), null, Map.of("email", bobEmail, "password", password), 200)
            .path("token")
            .asText();
    String digest =
        java.util.HexFormat.of()
            .formatHex(
                java.security.MessageDigest.getInstance("SHA-256")
                    .digest(token.getBytes(java.nio.charset.StandardCharsets.US_ASCII)));
    jdbc.update(
        "update "
            + SCHEMA
            + ".auth_session set expires_at=now()-interval '1 second' where token_hash=?",
        digest);
    request(get("/api/auth/me"), token, null, 401);
  }

  @Test
  void crudIsOwnerScopedAndRejectsOwnerInjection() throws Exception {
    var row = create(alice, "Salário", "crud", "99.10", "INCOME");
    String id = row.path("id").asText();
    assertThat(row.has("ownerId")).isFalse();
    assertThat(row.path("amount").isTextual()).isTrue();
    request(get("/api/transactions/" + id), bob, null, 404);
    request(
        put("/api/transactions/" + id),
        bob,
        movement("Roubo", "crud", "2.00", "EXPENSE", "2026-01-01"),
        404);
    request(delete("/api/transactions/" + id), bob, null, 404);
    request(
        put("/api/transactions/" + id),
        alice,
        movement("Editado", "crud", "10.20", "EXPENSE", "2099-01-01"),
        200);
    assertThat(
            request(get("/api/transactions/" + id), alice, null, 200).path("description").asText())
        .isEqualTo("Editado");
    var injected = new HashMap<>(movement("Teste", "crud", "1.00", "INCOME", "2026-01-01"));
    injected.put("ownerId", UUID.randomUUID().toString());
    request(post("/api/transactions"), alice, injected, 400);
    request(delete("/api/transactions/" + id), alice, null, 204);
    request(get("/api/transactions/" + id), alice, null, 404);
  }

  @Test
  void moneyAndRangesAreStrict() throws Exception {
    for (String amount : List.of("0", "-1", "1.001", "100000000000000.00", "NaN", "1e2"))
      request(
          post("/api/transactions"),
          alice,
          movement("Valor", "validation", amount, "INCOME", "2026-01-01"),
          400);
    var numeric = new HashMap<>(movement("Valor", "validation", "1.00", "INCOME", "2026-01-01"));
    numeric.put("amount", 1.00);
    request(post("/api/transactions"), alice, numeric, 400);
    request(
        post("/api/transactions"),
        alice,
        movement("Valor", "validation", "1.00", "OTHER", "2026-02-31"),
        400);
    request(
        get("/api/transactions").param("startDate", "2026-02-01").param("endDate", "2026-01-01"),
        alice,
        null,
        400);
    request(get("/api/transactions").param("startDate", "2026-02-31"), alice, null, 400);
    request(get("/api/transactions").param("endDate", "not-a-date"), alice, null, 400);
    request(
        get("/api/transactions/summary").param("minAmount", "2").param("maxAmount", "1"),
        alice,
        null,
        400);
    for (String size : List.of("0", "101", "x"))
      request(get("/api/transactions").param("size", size), alice, null, 400);
    request(get("/api/transactions").param("sort", "ownerId,asc"), alice, null, 400);
    var max = create(alice, "Limite", "max", "99999999999999.99", "INCOME");
    assertThat(max.path("amount").asText()).isEqualTo("99999999999999.99");
  }

  @Test
  void combinedFiltersLiteralLikePaginationAndTotals() throws Exception {
    String category = "filters-" + UUID.randomUUID();
    create(alice, "Bônus 100%_!", "" + category, "0.10", "INCOME");
    create(alice, "Bônus 100%_!", "" + category, "0.20", "INCOME");
    create(alice, "Bônus comum", category, "0.30", "EXPENSE");
    create(bob, "Bônus 100%_!", category, "999.00", "INCOME");
    var query =
        get("/api/transactions")
            .param("category", category)
            .param("type", "INCOME")
            .param("description", "100%_!")
            .param("startDate", "2026-06-15")
            .param("endDate", "2026-06-15")
            .param("minAmount", "0.10")
            .param("maxAmount", "0.20")
            .param("sort", "amount,asc")
            .param("size", "1");
    var page = request(query, alice, null, 200);
    assertThat(page.path("totalElements").asInt()).isEqualTo(2);
    assertThat(page.path("totalPages").asInt()).isEqualTo(2);
    assertThat(page.path("content").get(0).path("amount").asText()).isEqualTo("0.10");
    var summary =
        request(
            get("/api/transactions/summary")
                .param("category", category)
                .param("description", "100%_!")
                .param("size", "1"),
            alice,
            null,
            200);
    assertThat(summary.path("income").asText()).isEqualTo("0.30");
    assertThat(summary.path("expense").asText()).isEqualTo("0.00");
    assertThat(summary.path("count").asInt()).isEqualTo(2);
    var all =
        request(get("/api/transactions/summary").param("category", category), alice, null, 200);
    assertThat(all.path("balance").asText()).isEqualTo("0.00");
    var empty =
        request(
            get("/api/transactions/summary").param("category", UUID.randomUUID().toString()),
            alice,
            null,
            200);
    assertThat(empty.path("income").asText()).isEqualTo("0.00");
    assertThat(empty.path("count").asInt()).isZero();
  }

  @Test
  void deterministicDateTiesNeverRepeatAcrossPages() throws Exception {
    String category = "ties-" + UUID.randomUUID();
    for (int i = 0; i < 4; i++) create(alice, "Igual", category, "1.00", "INCOME");
    Set<String> ids = new HashSet<>();
    for (int page = 0; page < 4; page++) {
      var data =
          request(
              get("/api/transactions")
                  .param("category", category)
                  .param("page", String.valueOf(page))
                  .param("size", "1")
                  .param("sort", "date,asc"),
              alice,
              null,
              200);
      assertThat(ids.add(data.path("content").get(0).path("id").asText())).isTrue();
    }
  }

  @Test
  void pdfAndXlsxContainCompleteAuthorizedSelectionAndSafeText() throws Exception {
    String category = "exports-" + UUID.randomUUID();
    create(alice, "Ação € ç =1+1", category, "12.30", "INCOME");
    create(alice, "Saída útil", category, "2.10", "EXPENSE");
    create(bob, "SEGREDO-ALHEIO", category, "999.99", "INCOME");
    try (var document = Loader.loadPDF(file("export.pdf", alice, category))) {
      var text = new PDFTextStripper().getText(document);
      assertThat(text)
          .contains("Ação € ç =1+1", "12.30", "2.10", "10.20")
          .doesNotContain("SEGREDO-ALHEIO", "999.99");
    }
    try (var workbook =
        new XSSFWorkbook(new ByteArrayInputStream(file("export.xlsx", alice, category)))) {
      var sheet = workbook.getSheetAt(0);
      assertThat(sheet.getLastRowNum()).isEqualTo(6);
      var text = new StringBuilder();
      for (var row : sheet)
        for (var cell : row) {
          assertThat(cell.getCellType()).isEqualTo(CellType.STRING);
          text.append(cell.getStringCellValue()).append('|');
        }
      assertThat(text.toString())
          .contains("Ação € ç =1+1", "12.30", "2.10", "10.20")
          .doesNotContain("SEGREDO-ALHEIO", "999.99");
    }
  }

  @Test
  void pdfPaginatesLongDescriptionsAndRepeatsHeaders() throws Exception {
    String category = "pages-" + UUID.randomUUID();
    for (int i = 0; i < 18; i++)
      create(alice, "Descrição extensa " + "á".repeat(230), category, "1.00", "INCOME");
    try (var doc = Loader.loadPDF(file("export.pdf", alice, category))) {
      assertThat(doc.getNumberOfPages()).isGreaterThan(1);
      var stripper = new PDFTextStripper();
      for (int i = 1; i <= doc.getNumberOfPages(); i++) {
        stripper.setStartPage(i);
        stripper.setEndPage(i);
        assertThat(stripper.getText(doc)).contains("Movimentações financeiras");
      }
      stripper.setStartPage(1);
      stripper.setEndPage(doc.getNumberOfPages());
      assertThat(stripper.getText(doc)).contains("Entradas: 18.00");
    }
  }

  @Test
  void applicationMappingsHaveNoAffectedSseFragmentsOrXsltPaths() {
    var applicationMethods =
        mappings.getHandlerMethods().entrySet().stream()
            .filter(
                entry ->
                    entry
                        .getValue()
                        .getBeanType()
                        .getPackageName()
                        .startsWith("br.com.puck.finance"))
            .toList();
    assertThat(applicationMethods).hasSize(12);
    assertThat(
            applicationMethods.stream()
                .map(entry -> entry.getValue().getBeanType().getSimpleName())
                .distinct())
        .containsExactlyInAnyOrder("AuthREST", "TransactionREST");
    for (var entry : applicationMethods) {
      var method = entry.getValue().getMethod();
      assertThat(
              entry
                  .getValue()
                  .getBeanType()
                  .isAnnotationPresent(
                      org.springframework.web.bind.annotation.RestController.class))
          .isTrue();
      assertThat(method.getGenericReturnType().getTypeName())
          .doesNotContain(
              "SseEmitter",
              "ResponseBodyEmitter",
              "FragmentsRendering",
              "ModelAndView",
              "Xslt",
              "Publisher",
              "Flux");
      assertThat(method.getReturnType()).isNotEqualTo(String.class);
      assertThat(entry.getKey().getPatternValues())
          .allSatisfy(pattern -> assertThat(pattern).startsWith("/api/").doesNotContain("**"));
    }
    assertThat(context.getBeansOfType(org.springframework.web.servlet.view.xslt.XsltView.class))
        .isEmpty();
    assertThat(
            context.getBeansOfType(
                org.springframework.web.servlet.view.xslt.XsltViewResolver.class))
        .isEmpty();
  }

  @Test
  void concurrentDuplicateEmailIsConflict() throws Exception {
    String email = "race-" + UUID.randomUUID() + "@example.test";
    var body = Map.of("name", "Concorrência", "email", email, "password", password);
    var latch = new CountDownLatch(1);
    try (var executor = Executors.newFixedThreadPool(2)) {
      Callable<Integer> operation =
          () -> {
            latch.await();
            return mvc.perform(
                    post("/api/auth/register")
                        .contentType("application/json")
                        .content(json.writeValueAsBytes(body)))
                .andReturn()
                .getResponse()
                .getStatus();
          };
      var a = executor.submit(operation);
      var b = executor.submit(operation);
      latch.countDown();
      assertThat(List.of(a.get(), b.get())).containsExactlyInAnyOrder(201, 409);
    }
  }
}
