package br.com.puck.finance.transaction.actor;

import br.com.puck.finance.comum.ApiErrors.NotFound;
import br.com.puck.finance.transaction.dao.TransactionDAO;
import br.com.puck.finance.transaction.dominio.FinancialTransaction;
import br.com.puck.finance.transaction.dto.TransactionDtos.*;
import br.com.puck.finance.transaction.service.ExportService;
import br.com.puck.finance.transaction.service.TransactionRules;
import br.com.puck.finance.transaction.service.TransactionRules.Filter;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.*;

@Service
public class TransactionActor {
  private final TransactionDAO dao;
  private final ExportService exports;

  public TransactionActor(TransactionDAO dao, ExportService exports) {
    this.dao = dao;
    this.exports = exports;
  }

  @Transactional
  public Row create(UUID owner, Write input) {
    var row = new FinancialTransaction(owner);
    apply(row, input);
    return dto(dao.saveAndFlush(row));
  }

  @Transactional(readOnly = true)
  public Row get(UUID owner, UUID id) {
    return dto(owned(owner, id));
  }

  @Transactional
  public Row update(UUID owner, UUID id, Write input) {
    var row = owned(owner, id);
    apply(row, input);
    row.updatedAt = Instant.now();
    return dto(dao.saveAndFlush(row));
  }

  @Transactional
  public void delete(UUID owner, UUID id) {
    dao.delete(owned(owner, id));
  }

  @Transactional(readOnly = true, isolation = Isolation.REPEATABLE_READ)
  public Page list(UUID owner, Filter filter) {
    var result =
        dao.findAll(
            TransactionDAO.selection(owner, filter),
            PageRequest.of(filter.page(), filter.size(), TransactionDAO.sorting(filter)));
    return new Page(
        result.map(this::dto).getContent(),
        result.getTotalElements(),
        filter.page(),
        filter.size(),
        result.getTotalPages());
  }

  @Transactional(readOnly = true, isolation = Isolation.REPEATABLE_READ)
  public Summary summary(UUID owner, Filter filter) {
    return totals(selected(owner, filter));
  }

  @Transactional(readOnly = true, isolation = Isolation.REPEATABLE_READ)
  public byte[] export(UUID owner, Filter filter, boolean pdf) {
    var rows = selected(owner, filter);
    return pdf ? exports.pdf(rows, totals(rows)) : exports.xlsx(rows, totals(rows));
  }

  private List<Row> selected(UUID owner, Filter filter) {
    return dao
        .findAll(TransactionDAO.selection(owner, filter), TransactionDAO.sorting(filter))
        .stream()
        .map(this::dto)
        .toList();
  }

  private FinancialTransaction owned(UUID owner, UUID id) {
    return dao.findByIdAndOwnerId(id, owner).orElseThrow(NotFound::new);
  }

  private void apply(FinancialTransaction row, Write input) {
    row.type = input.type();
    row.description = TransactionRules.text(input.description(), 255);
    row.category = TransactionRules.text(input.category(), 80);
    row.amount = TransactionRules.amount(input.amount());
    row.date = input.date();
  }

  private Row dto(FinancialTransaction row) {
    return new Row(
        row.id,
        row.type,
        row.description,
        row.category,
        row.amount.toPlainString(),
        row.date,
        row.createdAt,
        row.updatedAt);
  }

  private Summary totals(List<Row> rows) {
    var income = new BigDecimal("0.00");
    var expense = new BigDecimal("0.00");
    for (var row : rows) {
      if (row.type() == FinancialTransaction.Type.INCOME)
        income = income.add(new BigDecimal(row.amount()));
      else expense = expense.add(new BigDecimal(row.amount()));
    }
    return new Summary(
        income.toPlainString(),
        expense.toPlainString(),
        income.subtract(expense).toPlainString(),
        rows.size());
  }
}
