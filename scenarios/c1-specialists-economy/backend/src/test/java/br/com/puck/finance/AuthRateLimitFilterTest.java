package br.com.puck.finance;

import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import static org.junit.jupiter.api.Assertions.assertEquals;

class AuthRateLimitFilterTest {
 @Test void encodedLoginPathsShareTheSameLimit() throws Exception {
  AuthRateLimitFilter filter = new AuthRateLimitFilter();
  for (int i=0; i<20; i++) assertEquals(200, request(filter, i%2==0 ? "/api/auth/login" : "/api/auth/%6Cogin", ""));
  assertEquals(429, request(filter, "/api/auth/%6cogin", ""));
 }
 @Test void encodedRegistrationPathsShareLimitWithContextPath() throws Exception {
  AuthRateLimitFilter filter = new AuthRateLimitFilter();
  for (int i=0; i<8; i++) assertEquals(200, request(filter, i%2==0 ? "/app/api/auth/register" : "/app/api/auth/%72egister", "/app"));
  assertEquals(429, request(filter, "/app/api/auth/register", "/app"));
  assertEquals(200, request(filter, "/app/api/auth/logout", "/app"));
 }
 private int request(AuthRateLimitFilter filter, String uri, String context) throws Exception {
  MockHttpServletRequest req=new MockHttpServletRequest("POST",uri); req.setContextPath(context); req.setRemoteAddr("192.0.2.1");
  MockHttpServletResponse response=new MockHttpServletResponse(); filter.doFilter(req,response,new MockFilterChain()); return response.getStatus();
 }
}
