package com.puck.finance;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.*;
@Entity @Table(name="app_user") class User { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; String name; @Column(unique=true) String email; @Column(name="password_hash") String passwordHash; }
@Entity @Table(name="session_token") class Session { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @Column(name="token_hash") String tokenHash; @Column(name="user_id") Long userId; @Column(name="expires_at") Instant expiresAt; }
@Entity @Table(name="transaction_record") class Entry { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) Long id; @Column(name="user_id") Long userId; String type; String description; String category; BigDecimal amount; LocalDate date; Instant createdAt; Instant updatedAt; }
