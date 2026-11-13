package br.com.puck.finance.transaction.service;

import br.com.puck.finance.transaction.dominio.FinancialTransaction.Type;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;

public final class TransactionRules {
  private TransactionRules() {}

  public static BigDecimal amount(String value) {
    var decimal = bound(value);
    if (decimal.signum() <= 0) throw new IllegalArgumentException();
    return decimal;
  }

  private static BigDecimal bound(String value) {
    if (value == null || !value.matches("[0-9]{1,14}(\\.[0-9]{1,2})?"))
      throw new IllegalArgumentException();
    return new BigDecimal(value).setScale(2);
  }

  public static String text(String value, int max) {
    if (value == null) throw new IllegalArgumentException();
    var cleaned = value.trim();
    if (cleaned.isEmpty()
        || cleaned.length() > max
        || cleaned.codePoints().anyMatch(Character::isISOControl))
      throw new IllegalArgumentException();
    return cleaned;
  }

  public record Filter(
      Type type,
      String category,
      String description,
      LocalDate startDate,
      LocalDate endDate,
      BigDecimal minAmount,
      BigDecimal maxAmount,
      String sortField,
      boolean ascending,
      int page,
      int size) {}

  public static Filter filter(Map<String, String> values) {
    var allowed =
        Set.of(
            "type",
            "category",
            "description",
            "startDate",
            "endDate",
            "minAmount",
            "maxAmount",
            "sort",
            "page",
            "size");
    if (!allowed.containsAll(values.keySet())) throw new IllegalArgumentException();
    var type = values.containsKey("type") ? Type.valueOf(values.get("type")) : null;
    String category = values.containsKey("category") ? text(values.get("category"), 80) : null;
    String description =
        values.containsKey("description") ? text(values.get("description"), 255) : null;
    LocalDate start =
        values.containsKey("startDate") ? LocalDate.parse(values.get("startDate")) : null;
    LocalDate end = values.containsKey("endDate") ? LocalDate.parse(values.get("endDate")) : null;
    BigDecimal min = values.containsKey("minAmount") ? bound(values.get("minAmount")) : null;
    BigDecimal max = values.containsKey("maxAmount") ? bound(values.get("maxAmount")) : null;
    if (start != null && end != null && start.isAfter(end)
        || min != null && max != null && min.compareTo(max) > 0)
      throw new IllegalArgumentException();
    String sort = values.getOrDefault("sort", "date,desc");
    if (!Set.of("date,desc", "date,asc", "amount,asc", "amount,desc").contains(sort))
      throw new IllegalArgumentException();
    int page = Integer.parseInt(values.getOrDefault("page", "0")),
        size = Integer.parseInt(values.getOrDefault("size", "20"));
    if (page < 0 || size < 1 || size > 100 || (long) page * size > Integer.MAX_VALUE)
      throw new IllegalArgumentException();
    return new Filter(
        type,
        category,
        description,
        start,
        end,
        min,
        max,
        sort.split(",")[0],
        sort.endsWith("asc"),
        page,
        size);
  }
}
