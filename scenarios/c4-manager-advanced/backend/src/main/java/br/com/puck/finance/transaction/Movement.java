package br.com.puck.finance.transaction;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.UUID;
@Entity @Table(name="movement")
public class Movement {
 public enum Type {INCOME,EXPENSE}
 @Id public UUID id;
 @Column(nullable=false) public UUID ownerId;
 @Enumerated(EnumType.STRING) @Column(nullable=false,length=7) public Type type;
 @Column(nullable=false,length=255) public String description;
 @Column(nullable=false,length=80) public String category;
 @Column(nullable=false,precision=16,scale=2) public BigDecimal amount;
 @Column(nullable=false) public LocalDate date;
 @Column(nullable=false) public Instant createdAt;
 @Column(nullable=false) public Instant updatedAt;
 protected Movement(){}
 public Movement(UUID owner){id=UUID.randomUUID();ownerId=owner;createdAt=Instant.now();updatedAt=createdAt;}
}
