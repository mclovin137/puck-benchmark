package br.com.puck.finance.auth;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
@Configuration
public class Security {
 @Bean SecurityFilterChain chain(HttpSecurity http,AuthActor auth)throws Exception{
  return http.csrf(c->c.disable()).sessionManagement(c->c.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
   .authorizeHttpRequests(c->c.requestMatchers(org.springframework.http.HttpMethod.POST,"/api/auth/register","/api/auth/login").permitAll().anyRequest().authenticated())
   .exceptionHandling(c->c.authenticationEntryPoint((q,r,e)->{r.setStatus(401);r.setContentType("application/json");r.setCharacterEncoding(StandardCharsets.UTF_8.name());r.getWriter().write("{\"message\":\"Faça login para continuar.\"}");}))
   .headers(c->c.contentSecurityPolicy(p->p.policyDirectives("default-src 'none'; frame-ancestors 'none'")))
   .addFilterBefore(new OncePerRequestFilter(){protected void doFilterInternal(HttpServletRequest q,HttpServletResponse r,FilterChain chain)throws ServletException,IOException{
    String h=q.getHeader("Authorization");
    if(h!=null&&h.startsWith("Bearer ")&&h.length()<256)auth.authenticate(h.substring(7)).ifPresent(id->SecurityContextHolder.getContext().setAuthentication(new UsernamePasswordAuthenticationToken(id,null,List.of())));
    chain.doFilter(q,r);
   }},UsernamePasswordAuthenticationFilter.class).build();
 }
}
