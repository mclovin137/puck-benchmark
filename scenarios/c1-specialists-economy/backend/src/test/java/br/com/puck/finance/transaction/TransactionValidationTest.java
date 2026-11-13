package br.com.puck.finance;

import br.com.puck.finance.*;
import br.com.puck.finance.Models.Entry;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TransactionValidationTest {
 @Test void rejectsUnknownTypeAndNonPositiveAmounts(){
  TransactionService service=new TransactionService(mock(Entries.class),mock(Identity.class));
  TxRequest good=new TxRequest("TRANSFER","Despesa","Casa",new BigDecimal("12.00"),LocalDate.now());
  ApiError type=assertThrows(ApiError.class,()->service.create(new TxRequest("TRANSFER",good.description(),good.category(),good.amount(),good.date())));
  assertEquals(HttpStatus.BAD_REQUEST,type.status);
  ApiError amount=assertThrows(ApiError.class,()->service.create(new TxRequest("EXPENSE",good.description(),good.category(),BigDecimal.ZERO,good.date())));
  assertEquals(HttpStatus.BAD_REQUEST,amount.status);
 }
 @Test void rejectsMissingIdentityBeforePersisting(){
  Entries entries=mock(Entries.class);Identity identity=mock(Identity.class);when(identity.get()).thenReturn(null);
  TransactionService service=new TransactionService(entries,identity);
  TxRequest request=new TxRequest("INCOME","Salário","Trabalho",new BigDecimal("1.00"),LocalDate.now());
  ApiError error=assertThrows(ApiError.class,()->service.create(request));assertEquals(HttpStatus.UNAUTHORIZED,error.status);verifyNoInteractions(entries);
 }
}
