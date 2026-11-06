package br.com.puck.finance.auth.dto;

import jakarta.validation.constraints.*;
import java.util.UUID;

public final class AuthDtos {
  private AuthDtos() {}

  public record Register(
      @NotNull String name,
      @NotNull String email,
      @NotNull @Size(min = 12, max = 128) String password) {}

  public record Login(@NotNull String email, @NotNull @Size(max = 128) String password) {}

  public record User(UUID id, String name, String email) {}

  public record Token(String token) {}
}
