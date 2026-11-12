package br.com.puck.finance;

import br.com.puck.finance.auth.AuthActor;
import br.com.puck.finance.auth.AuthREST;
import br.com.puck.finance.auth.Security;
import br.com.puck.finance.common.ApiError;
import br.com.puck.finance.common.Errors;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.mock.web.MockServletContext;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import static org.springframework.security.test.web.servlet.setup.SecurityMockMvcConfigurers.springSecurity;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/** Regressões autorais de contrato na fronteira MVC/Security; sem banco ou rede. */
class AuthContractTest {
 @Configuration @EnableWebMvc @EnableWebSecurity
 @Import({Security.class, AuthREST.class, Errors.class})
 static class WebConfig {
  @Bean StubAuthActor authActor() { return new StubAuthActor(); }
 }
 static class StubAuthActor extends AuthActor {
  int loginCalls;
  StubAuthActor() { super(null,null); }
  @Override public Optional<java.util.UUID> authenticate(String token) { return Optional.empty(); }
  @Override public Map<String,String> login(Login request) {
   loginCalls++;
   if(request.password().equals("long-example-password"))return Map.of("token","synthetic-contract-token");
   throw new ApiError(HttpStatus.UNAUTHORIZED,"E-mail ou senha inválidos.");
  }
  @Override public Profile register(Register request) { throw new AssertionError("Cadastro inválido atingiu o actor"); }
 }
 AnnotationConfigWebApplicationContext context;
 MockMvc api;
 ObjectMapper json=new ObjectMapper();
 StubAuthActor actor;
 @BeforeEach void setup() {
  context=new AnnotationConfigWebApplicationContext();
  context.setServletContext(new MockServletContext());
  context.register(WebConfig.class);context.refresh();
  actor=context.getBean(StubAuthActor.class);
  api=MockMvcBuilders.webAppContextSetup(context).apply(springSecurity()).build();
 }
 @AfterEach void close() { context.close(); }

 @Test void unauthorizedResponsesAreStrictUtf8Json() throws Exception {
  for(String path:new String[]{"/api/auth/me","/api/transactions","/api/transactions/export.pdf","/api/transactions/export.xlsx"}) {
   for(String token:new String[]{"","expired"}) {
    var request=get(path);
    if(!token.isEmpty())request.header("Authorization","Bearer "+token);
    var response=api.perform(request).andExpect(status().isUnauthorized())
     .andExpect(content().contentTypeCompatibleWith("application/json")).andReturn().getResponse();
    String body=StandardCharsets.UTF_8.newDecoder()
     .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT)
     .decode(ByteBuffer.wrap(response.getContentAsByteArray())).toString();
    assertEquals("Faça login para continuar.",json.readTree(body).get("message").asText());
   }
  }
 }

 @Test void tomcatUnauthorizedWriterProducesStrictUtf8Bytes() throws Exception {
  var sink=new java.io.ByteArrayOutputStream();
  var coyote=new org.apache.coyote.Response();
  coyote.setOutputBuffer(new org.apache.coyote.OutputBuffer() {
   public int doWrite(ByteBuffer chunk) {
    int count=chunk.remaining();byte[] bytes=new byte[count];chunk.get(bytes);sink.writeBytes(bytes);return count;
   }
   public long getBytesWritten() { return sink.size(); }
  });
  var response=new org.apache.catalina.connector.Response();response.setCoyoteResponse(coyote);
  var request=new org.apache.catalina.connector.Request(new org.apache.catalina.connector.Connector());
  request.setCoyoteRequest(new org.apache.coyote.Request());request.setResponse(response);response.setRequest(request);
  var chain=context.getBean(org.springframework.security.web.SecurityFilterChain.class);
  var entryPoint=chain.getFilters().stream()
   .filter(org.springframework.security.web.access.ExceptionTranslationFilter.class::isInstance)
   .map(org.springframework.security.web.access.ExceptionTranslationFilter.class::cast)
   .findFirst().orElseThrow().getAuthenticationEntryPoint();
  entryPoint.commence(new org.springframework.mock.web.MockHttpServletRequest(),response.getResponse(),
   new org.springframework.security.authentication.InsufficientAuthenticationException("missing"));
  response.flushBuffer();
  assertEquals(401,response.getStatus());
  String body=assertDoesNotThrow(()->StandardCharsets.UTF_8.newDecoder()
   .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT)
   .decode(ByteBuffer.wrap(sink.toByteArray())).toString());
  assertEquals("Faça login para continuar.",json.readTree(body).get("message").asText());
 }

 @Test void shortIncorrectLoginPasswordReachesCredentialCheck() throws Exception {
  for(String password:new String[]{"x","","different-long-password"}) {
   api.perform(post("/api/auth/login").contentType("application/json")
    .content(json.writeValueAsString(Map.of("email","person@example.test","password",password))))
    .andExpect(status().isUnauthorized());
  }
  assertEquals(3,actor.loginCalls);
 }

 @Test void registrationMinimumAndMalformedLoginRemainValidationErrors() throws Exception {
  api.perform(post("/api/auth/register").contentType("application/json")
   .content("{\"name\":\"Pessoa\",\"email\":\"person@example.test\",\"password\":\"x\"}"))
   .andExpect(status().isBadRequest());
  for(String body:new String[]{"{\"email\":\"person@example.test\"}","{\"email\":\"invalid\",\"password\":\"x\"}"}) {
   api.perform(post("/api/auth/login").contentType("application/json").content(body))
    .andExpect(status().isBadRequest());
  }
  api.perform(post("/api/auth/login").contentType("application/json")
   .content(json.writeValueAsString(Map.of("email","person@example.test","password","x".repeat(129)))))
   .andExpect(status().isBadRequest());
  assertEquals(0,actor.loginCalls);
 }

 @Test void validLoginResponseIsUnchanged() throws Exception {
  api.perform(post("/api/auth/login").contentType("application/json")
   .content("{\"email\":\"person@example.test\",\"password\":\"long-example-password\"}"))
   .andExpect(status().isOk()).andExpect(jsonPath("$.token").value("synthetic-contract-token"));
 }
}
