package br.com.puck.finance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@SpringBootApplication
public class Application {
  public static void main(String[] args) { SpringApplication.run(Application.class, args); }
  @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(12); }
  @Bean WebMvcConfigurer cors() { return new WebMvcConfigurer() { public void addCorsMappings(CorsRegistry r) { r.addMapping("/api/**").allowedOrigins(System.getenv().getOrDefault("CORS_ORIGIN", "http://localhost:5173")).allowedMethods("GET","POST","PUT","DELETE","OPTIONS").allowedHeaders("Authorization","Content-Type"); } }; }
}
