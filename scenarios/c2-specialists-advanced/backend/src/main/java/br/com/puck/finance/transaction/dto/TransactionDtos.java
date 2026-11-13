package br.com.puck.finance.transaction.dto;

import br.com.puck.finance.transaction.dominio.FinancialTransaction.Type;
import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import jakarta.validation.constraints.*;
import java.io.IOException;
import java.time.*;
import java.util.*;

public final class TransactionDtos {
  private TransactionDtos() {}

  public static class DecimalString extends JsonDeserializer<String> {
    @Override
    public String deserialize(JsonParser p, DeserializationContext context) throws IOException {
      if (!p.hasToken(JsonToken.VALUE_STRING))
        return (String) context.handleUnexpectedToken(String.class, p);
      return p.getText();
    }
  }

  public record Write(
      @NotNull Type type,
      @NotNull String description,
      @NotNull String category,
      @NotNull @JsonDeserialize(using = DecimalString.class) String amount,
      @NotNull LocalDate date) {}

  public record Row(
      UUID id,
      Type type,
      String description,
      String category,
      String amount,
      LocalDate date,
      Instant createdAt,
      Instant updatedAt) {}

  public record Page(List<Row> content, long totalElements, int page, int size, int totalPages) {}

  public record Summary(String income, String expense, String balance, long count) {}
}
