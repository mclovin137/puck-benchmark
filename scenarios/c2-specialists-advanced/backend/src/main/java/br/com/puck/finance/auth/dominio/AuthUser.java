package br.com.puck.finance.auth.dominio;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "app_user")
public class AuthUser {
  @Id public UUID id;

  @Column(nullable = false, length = 120)
  public String name;

  @Column(nullable = false, unique = true, length = 254)
  public String email;

  @Column(name = "password_hash", nullable = false)
  public String passwordHash;

  @Column(name = "created_at", nullable = false)
  public Instant createdAt;

  public AuthUser() {}

  public AuthUser(String name, String email, String passwordHash) {
    this.id = UUID.randomUUID();
    this.name = name;
    this.email = email;
    this.passwordHash = passwordHash;
    this.createdAt = Instant.now();
  }
}
