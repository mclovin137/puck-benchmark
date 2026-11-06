package br.com.puck.finance.transaction.dominio;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.UUID;

@Entity
@Table(name = "financial_transaction")
public class FinancialTransaction {
  public enum Type {
    INCOME,
    EXPENSE
  }

  @Id public UUID id;

  @Column(name = "owner_id", nullable = false)
  public UUID ownerId;

  @Enumerated(EnumType.STRING)
  @Column(nullable = false, length = 7)
  public Type type;

  @Column(nullable = false, length = 255)
  public String description;

  @Column(nullable = false, length = 80)
  public String category;

  @Column(nullable = false, precision = 16, scale = 2)
  public BigDecimal amount;

  @Column(nullable = false)
  public LocalDate date;

  @Column(name = "created_at", nullable = false)
  public Instant createdAt;

  @Column(name = "updated_at", nullable = false)
  public Instant updatedAt;

  public FinancialTransaction() {}

  public FinancialTransaction(UUID ownerId) {
    this.id = UUID.randomUUID();
    this.ownerId = ownerId;
    this.createdAt = Instant.now();
    this.updatedAt = createdAt;
  }
}
