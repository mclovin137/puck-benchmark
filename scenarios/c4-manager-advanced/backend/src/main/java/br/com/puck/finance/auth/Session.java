package br.com.puck.finance.auth;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;
@Entity @Table(name="auth_session")
public class Session {
 @Id @Column(length=64) public String tokenHash;
 @Column(nullable=false) public UUID ownerId;
 @Column(nullable=false) public Instant expiresAt;
 protected Session() {}
 public Session(String hash,UUID owner) { tokenHash=hash;ownerId=owner;expiresAt=Instant.now().plusSeconds(28800); }
}
