package br.com.puck.finance;
import com.fasterxml.jackson.databind.*;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.*;
import org.springframework.test.context.*;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.*;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import java.io.*;
import java.util.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.junit.jupiter.api.Assertions.*;
@SpringBootTest @AutoConfigureMockMvc @Testcontainers
class ApiIntegrationTest {
 @Container static PostgreSQLContainer<?> postgres=new PostgreSQLContainer<>("postgres:17.11");
 @DynamicPropertySource static void props(DynamicPropertyRegistry r){r.add("spring.datasource.url",postgres::getJdbcUrl);r.add("spring.datasource.username",postgres::getUsername);r.add("spring.datasource.password",postgres::getPassword);}
 @Autowired MockMvc api;@Autowired ObjectMapper json;
 String register(String email)throws Exception{api.perform(post("/api/auth/register").contentType("application/json").content(json.writeValueAsString(Map.of("name","Pessoa","email",email,"password","long-example-password")))).andExpect(status().isCreated());return login(email);}
 String login(String email)throws Exception{return json.readTree(api.perform(post("/api/auth/login").contentType("application/json").content(json.writeValueAsString(Map.of("email",email,"password","long-example-password")))).andExpect(status().isOk()).andReturn().getResponse().getContentAsString()).get("token").asText();}
 String create(String token,String type,String desc,String category,String amount,String date)throws Exception{return json.readTree(api.perform(post("/api/transactions").header("Authorization","Bearer "+token).contentType("application/json").content(json.writeValueAsString(Map.of("type",type,"description",desc,"category",category,"amount",amount,"date",date)))).andExpect(status().isCreated()).andReturn().getResponse().getContentAsString()).get("id").asText();}
 @Test void authorizationCrudFiltersExportsAndRevocation()throws Exception{
  String a=register("owner@example.test"),b=register("other@example.test");
  String id=create(a,"INCOME","Salário 100%_","Trabalho","1000.10","2026-01-10");create(a,"EXPENSE","Mercado","Casa","100.05","2026-01-10");create(a,"INCOME","Extra","Trabalho","5.20","2026-02-01");create(b,"INCOME","Segredo","Privado","999.99","2026-01-10");
  api.perform(get("/api/transactions/"+id)).andExpect(status().isUnauthorized());
  for(var req:List.of(get("/api/transactions/"+id),delete("/api/transactions/"+id)))api.perform(req.header("Authorization","Bearer "+b)).andExpect(status().isNotFound());
  api.perform(put("/api/transactions/"+id).header("Authorization","Bearer "+b).contentType("application/json").content("{\"type\":\"INCOME\",\"description\":\"X\",\"category\":\"X\",\"amount\":\"1.00\",\"date\":\"2026-01-10\"}")).andExpect(status().isNotFound());
  api.perform(get("/api/transactions").header("Authorization","Bearer "+a).param("size","1").param("sort","amount,asc")).andExpect(jsonPath("$.totalElements").value(3)).andExpect(jsonPath("$.totalPages").value(3)).andExpect(jsonPath("$.content[0].amount").value("5.20"));
  String filter="?startDate=2026-01-10&endDate=2026-01-10";
  api.perform(get("/api/transactions/summary"+filter).header("Authorization","Bearer "+a)).andExpect(jsonPath("$.income").value("1000.10")).andExpect(jsonPath("$.expense").value("100.05")).andExpect(jsonPath("$.balance").value("900.05")).andExpect(jsonPath("$.count").value(2));
  api.perform(get("/api/transactions").header("Authorization","Bearer "+a).param("description","100%_").param("category","Trabalho").param("type","INCOME").param("minAmount","1000.10").param("maxAmount","1000.10")).andExpect(jsonPath("$.totalElements").value(1));
  byte[] pdf=api.perform(get("/api/transactions/export.pdf"+filter).header("Authorization","Bearer "+a)).andExpect(status().isOk()).andExpect(content().contentType("application/pdf")).andReturn().getResponse().getContentAsByteArray();
  try(var doc=Loader.loadPDF(pdf)){String text=new PDFTextStripper().getText(doc);assertTrue(text.contains("Salário 100%_"));assertTrue(text.contains("900.05"));assertTrue(text.contains("100.05"));assertFalse(text.contains("Segredo"));assertFalse(text.contains("Extra"));}
  byte[] xlsx=api.perform(get("/api/transactions/export.xlsx"+filter).header("Authorization","Bearer "+a)).andExpect(status().isOk()).andReturn().getResponse().getContentAsByteArray();
  try(var wb=new XSSFWorkbook(new ByteArrayInputStream(xlsx))){var sh=wb.getSheetAt(0);assertEquals(6,sh.getLastRowNum());assertEquals("1000.10",sh.getRow(3).getCell(4).getStringCellValue());assertEquals("900.05",sh.getRow(5).getCell(4).getStringCellValue());}
  api.perform(get("/api/transactions").header("Authorization","Bearer "+a).param("startDate","2026-02-01").param("endDate","2026-01-01")).andExpect(status().isBadRequest());
  api.perform(get("/api/transactions").header("Authorization","Bearer "+a).param("sort","ownerId,asc")).andExpect(status().isBadRequest());
  api.perform(get("/api/transactions").header("Authorization","Bearer "+a).param("minAmount","5").param("maxAmount","1")).andExpect(status().isBadRequest());
  api.perform(post("/api/auth/logout").header("Authorization","Bearer "+a)).andExpect(status().isNoContent());api.perform(get("/api/auth/me").header("Authorization","Bearer "+a)).andExpect(status().isUnauthorized());
 }
 @Test void validatesRegistrationAndFinancialBoundary()throws Exception{
  String a=register("validation@example.test");
  api.perform(post("/api/auth/register").contentType("application/json").content("{\"name\":\"Pessoa\",\"email\":\"VALIDATION@example.test\",\"password\":\"long-example-password\"}")).andExpect(status().isConflict());
  api.perform(post("/api/auth/login").contentType("application/json").content("{\"email\":\"validation@example.test\",\"password\":\"wrong-example-password\"}")).andExpect(status().isUnauthorized());
  for(String amount:List.of("0","-1","1.001","100000000000000.00"))api.perform(post("/api/transactions").header("Authorization","Bearer "+a).contentType("application/json").content(json.writeValueAsString(Map.of("type","INCOME","description","test","category","test","amount",amount,"date","2026-01-01")))).andExpect(status().isBadRequest());
  api.perform(post("/api/transactions").header("Authorization","Bearer "+a).contentType("application/json").content("{\"type\":\"INCOME\",\"description\":\"test\",\"category\":\"test\",\"amount\":1.2,\"date\":\"2026-01-01\"}")).andExpect(status().isBadRequest());
  create(a,"INCOME","Máximo","Limite","99999999999999.99","2099-01-01");
  api.perform(get("/api/transactions/summary").header("Authorization","Bearer "+a)).andExpect(jsonPath("$.balance").value("99999999999999.99"));
 }
}
