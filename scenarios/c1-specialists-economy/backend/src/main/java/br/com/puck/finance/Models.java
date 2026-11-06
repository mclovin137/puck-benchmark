package br.com.puck.finance;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.UUID;

public final class Models {
  private Models() {}
  @Entity @Table(name="app_user") public static class User {
    @Id public UUID id; @Column(nullable=false,length=120) public String name; @Column(nullable=false,unique=true,length=254) public String email; @Column(name="password_hash",nullable=false,length=100) public String passwordHash; @Column(name="created_at",nullable=false) public OffsetDateTime createdAt=OffsetDateTime.now(ZoneOffset.UTC);
    protected User() {} public User(String n,String e,String p){id=UUID.randomUUID();name=n;email=e;passwordHash=p;}
  }
  @Entity(name="AuthToken") @Table(name="auth_token") public static class Token {
    @Id @Column(name="token_hash",length=64) public String tokenHash; @Column(name="user_id",nullable=false) public UUID userId; @Column(name="expires_at",nullable=false) public OffsetDateTime expiresAt; @Column(name="revoked_at") public OffsetDateTime revokedAt;
    protected Token() {} public Token(String h,UUID u,OffsetDateTime e){tokenHash=h;userId=u;expiresAt=e;}
  }
  @Entity(name="TransactionEntry") @Table(name="transaction_entry") public static class Entry {
    @Id public UUID id; @Column(name="user_id",nullable=false) public UUID userId; @Column(nullable=false,length=7) public String type; @Column(nullable=false,length=255) public String description; @Column(nullable=false,length=80) public String category; @Column(nullable=false,precision=16,scale=2) public BigDecimal amount; @Column(name="entry_date",nullable=false) public LocalDate date; @Column(name="created_at",nullable=false) public OffsetDateTime createdAt; @Column(name="updated_at",nullable=false) public OffsetDateTime updatedAt;
    protected Entry() {} public Entry(UUID u, String t,String d,String c,BigDecimal a,LocalDate date){this.id=UUID.randomUUID();this.userId=u;this.type=t;this.description=d;this.category=c;this.amount=a;this.date=date;this.createdAt=OffsetDateTime.now(ZoneOffset.UTC);this.updatedAt=createdAt;}
  }
}
