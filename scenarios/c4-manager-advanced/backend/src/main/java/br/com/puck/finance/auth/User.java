package br.com.puck.finance.auth;
import jakarta.persistence.*;
import java.util.UUID;
@Entity @Table(name="app_user")
public class User {
 @Id public UUID id;
 @Column(nullable=false,length=120) public String name;
 @Column(nullable=false,unique=true,length=254) public String email;
 @Column(nullable=false,length=255) public String passwordHash;
 protected User() {}
 public User(String name,String email,String hash) { this.id=UUID.randomUUID();this.name=name;this.email=email;this.passwordHash=hash; }
}
