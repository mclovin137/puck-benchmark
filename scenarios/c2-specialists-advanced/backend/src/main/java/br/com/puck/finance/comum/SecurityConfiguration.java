package br.com.puck.finance.comum;

import br.com.puck.finance.auth.actor.AuthActor;
import br.com.puck.finance.comum.ApiErrors.Unauthorized;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.*;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.*;
import org.springframework.web.filter.OncePerRequestFilter;

@Configuration
public class SecurityConfiguration {
  @Bean
  SecurityFilterChain security(
      HttpSecurity http, AuthActor auth, @Value("${app.cors-origin}") String origin)
      throws Exception {
    var cors = new CorsConfiguration();
    cors.setAllowedOrigins(List.of(origin));
    cors.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    cors.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    cors.setExposedHeaders(List.of("Content-Disposition"));
    var source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", cors);
    http.csrf(c -> c.disable())
        .cors(c -> c.configurationSource(source))
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .requestCache(c -> c.disable())
        .formLogin(c -> c.disable())
        .httpBasic(c -> c.disable())
        .logout(c -> c.disable());
    http.authorizeHttpRequests(
        a ->
            a.requestMatchers(HttpMethod.POST, "/api/auth/register", "/api/auth/login")
                .permitAll()
                .requestMatchers(HttpMethod.OPTIONS, "/api/**")
                .permitAll()
                .anyRequest()
                .authenticated());
    http.exceptionHandling(
        e ->
            e.authenticationEntryPoint((req, res, ex) -> unauthorized(res))
                .accessDeniedHandler((req, res, ex) -> unauthorized(res)));
    http.addFilterBefore(
        new OncePerRequestFilter() {
          @Override
          protected void doFilterInternal(
              HttpServletRequest request, HttpServletResponse response, FilterChain chain)
              throws ServletException, IOException {
            String header = request.getHeader("Authorization");
            if (header != null) {
              try {
                if (!header.startsWith("Bearer ")) throw new Unauthorized();
                var principal = auth.authenticate(header.substring(7));
                var authentication =
                    new UsernamePasswordAuthenticationToken(principal, null, List.of());
                SecurityContextHolder.getContext().setAuthentication(authentication);
              } catch (Unauthorized ex) {
                unauthorized(response);
                return;
              }
            }
            chain.doFilter(request, response);
          }
        },
        UsernamePasswordAuthenticationFilter.class);
    return http.build();
  }

  private static void unauthorized(HttpServletResponse response) throws IOException {
    response.setStatus(401);
    response.setCharacterEncoding(java.nio.charset.StandardCharsets.UTF_8.name());
    response.setContentType("application/json");
    response.getWriter().write("{\"message\":\"Autenticação necessária\"}");
  }
}
