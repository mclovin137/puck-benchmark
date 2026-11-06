package br.com.puck.finance.auth.dominio;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "auth_session")
public class AuthSession {
  @Id public UUID id;

  @Column(name = "user_id", nullable = false)
  public UUID userId;

  @Column(name = "token_hash", nullable = false, unique = true, length = 64)
  public String tokenHash;

  @Column(name = "expires_at", nullable = false)
  public Instant expiresAt;

  @Column(name = "revoked_at")
  public Instant revokedAt;

  public AuthSession() {}

  public AuthSession(UUID userId, String tokenHash) {
    this.id = UUID.randomUUID();
    this.userId = userId;
    this.tokenHash = tokenHash;
    this.expiresAt = Instant.now().plusSeconds(43200);
  }
}
