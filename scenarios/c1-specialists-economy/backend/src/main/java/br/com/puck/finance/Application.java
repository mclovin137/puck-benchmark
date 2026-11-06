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
  @Bean PasswordEncoder passwordEncoder() { return new PasswordEncoder() {
    private final BCryptPasswordEncoder bcrypt = new BCryptPasswordEncoder(12);
    private String digest(CharSequence raw) { try { return java.util.Base64.getEncoder().encodeToString(java.security.MessageDigest.getInstance("SHA-256").digest(raw.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8))); } catch (java.security.NoSuchAlgorithmException e) { throw new IllegalStateException(e); } }
    public String encode(CharSequence raw) { return "{bcrypt-sha256}" + bcrypt.encode(digest(raw)); }
    public boolean matches(CharSequence raw, String encoded) { if (encoded.startsWith("{bcrypt-sha256}")) return bcrypt.matches(digest(raw), encoded.substring(15)); try { return bcrypt.matches(raw, encoded); } catch (IllegalArgumentException e) { return false; } }
  }; }
  @Bean WebMvcConfigurer cors() { return new WebMvcConfigurer() { public void addCorsMappings(CorsRegistry r) { r.addMapping("/api/**").allowedOrigins(System.getenv().getOrDefault("CORS_ORIGIN", "http://localhost:5173")).allowedMethods("GET","POST","PUT","DELETE","OPTIONS").allowedHeaders("Authorization","Content-Type"); } }; }
}
