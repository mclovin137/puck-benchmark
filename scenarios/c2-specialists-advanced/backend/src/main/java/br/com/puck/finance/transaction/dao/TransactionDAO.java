package br.com.puck.finance.transaction.dao;

import br.com.puck.finance.transaction.dominio.FinancialTransaction;
import br.com.puck.finance.transaction.service.TransactionRules.Filter;
import jakarta.persistence.criteria.Predicate;
import java.util.*;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.data.jpa.repository.*;

public interface TransactionDAO
    extends JpaRepository<FinancialTransaction, UUID>,
        JpaSpecificationExecutor<FinancialTransaction> {
  Optional<FinancialTransaction> findByIdAndOwnerId(UUID id, UUID ownerId);

  static Specification<FinancialTransaction> selection(UUID ownerId, Filter f) {
    Objects.requireNonNull(ownerId);
    return (root, query, cb) -> {
      var predicates = new ArrayList<Predicate>();
      predicates.add(cb.equal(root.get("ownerId"), ownerId));
      if (f.type() != null) predicates.add(cb.equal(root.get("type"), f.type()));
      if (f.category() != null) predicates.add(cb.equal(root.get("category"), f.category()));
      if (f.description() != null) {
        var literal =
            f.description()
                .toLowerCase(Locale.ROOT)
                .replace("!", "!!")
                .replace("%", "!%")
                .replace("_", "!_");
        predicates.add(cb.like(cb.lower(root.get("description")), "%" + literal + "%", '!'));
      }
      if (f.startDate() != null)
        predicates.add(cb.greaterThanOrEqualTo(root.get("date"), f.startDate()));
      if (f.endDate() != null) predicates.add(cb.lessThanOrEqualTo(root.get("date"), f.endDate()));
      if (f.minAmount() != null)
        predicates.add(cb.greaterThanOrEqualTo(root.get("amount"), f.minAmount()));
      if (f.maxAmount() != null)
        predicates.add(cb.lessThanOrEqualTo(root.get("amount"), f.maxAmount()));
      return cb.and(predicates.toArray(Predicate[]::new));
    };
  }

  static Sort sorting(Filter f) {
    return Sort.by(f.ascending() ? Sort.Direction.ASC : Sort.Direction.DESC, f.sortField())
        .and(Sort.by("id"));
  }
}
