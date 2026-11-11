package br.com.puck.finance.transaction;
import br.com.puck.finance.common.ApiError;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.data.domain.PageRequest;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;
@Service @Transactional(readOnly=true)
public class TransactionActor {
 private final MovementDAO dao;
 public TransactionActor(MovementDAO dao){this.dao=dao;}
 private Movement owned(UUID owner,UUID id){return dao.findByIdAndOwnerId(id,owner).orElseThrow(ApiError::missing);}
 private void apply(Movement m,TransactionDTO.Input r){m.type=r.type();m.description=FinancialRules.text(r.description(),255);m.category=FinancialRules.text(r.category(),80);m.amount=FinancialRules.amount(r.amount());try{m.date=LocalDate.parse(r.date());}catch(DateTimeException e){throw ApiError.invalid("Data inválida.");}m.updatedAt=Instant.now();}
 @Transactional public TransactionDTO.Row create(UUID owner,TransactionDTO.Input r){Movement m=new Movement(owner);apply(m,r);return TransactionDTO.Row.from(dao.save(m));}
 public TransactionDTO.Row get(UUID owner,UUID id){return TransactionDTO.Row.from(owned(owner,id));}
 @Transactional public TransactionDTO.Row update(UUID owner,UUID id,TransactionDTO.Input r){Movement m=owned(owner,id);apply(m,r);return TransactionDTO.Row.from(dao.save(m));}
 @Transactional public void delete(UUID owner,UUID id){dao.delete(owned(owner,id));}
 public TransactionDTO.Listing list(Selection s){var p=dao.findAll(s.predicate(),PageRequest.of(s.page(),s.size(),s.sort()));return new TransactionDTO.Listing(p.getContent().stream().map(TransactionDTO.Row::from).toList(),p.getTotalElements(),s.page(),s.size(),p.getTotalPages());}
 public List<TransactionDTO.Row> rows(Selection s){return dao.findAll(s.predicate(),s.sort()).stream().map(TransactionDTO.Row::from).toList();}
 public TransactionDTO.Summary summary(Selection s){return total(rows(s));}
 public static TransactionDTO.Summary total(List<TransactionDTO.Row> rows){BigDecimal income=new BigDecimal("0.00"),expense=income;for(var row:rows){if(row.type()==Movement.Type.INCOME)income=income.add(new BigDecimal(row.amount()));else expense=expense.add(new BigDecimal(row.amount()));}return new TransactionDTO.Summary(income.toPlainString(),expense.toPlainString(),income.subtract(expense).toPlainString(),rows.size());}
}
