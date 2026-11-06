package br.com.puck.finance;

import br.com.puck.finance.Models.Entry;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class TransactionExportTest {
 @Test void pdfStreamsAllPagesAndKeepsOwnerScope() throws Exception {
  UUID owner=UUID.randomUUID(); Identity identity=mock(Identity.class); when(identity.get()).thenReturn(owner);
  Entries entries=mock(Entries.class); List<Entry> first=new ArrayList<>();
  for(int i=0;i<500;i++) first.add(entry(owner,"item-"+i));
  Entry last=entry(owner,"last-record-500");
  when(entries.filtered(eq(owner),any(),any(),any(),any(),any(),any(),any(),any(Pageable.class))).thenAnswer(call->{Pageable p=call.getArgument(8);return p.getPageNumber()==0?new PageImpl<>(first,p,501):new PageImpl<>(List.of(last),p,501);});
  TransactionService service=new TransactionService(entries,identity); ByteArrayOutputStream bytes=new ByteArrayOutputStream();
  service.export(Map.of(),false).writeTo(bytes);
  try(var pdf=Loader.loadPDF(bytes.toByteArray())) {String text=new PDFTextStripper().getText(pdf);assertTrue(text.contains("item-0"));assertTrue(text.contains("last-record-500"));assertEquals(501, countOccurrences(text,"Categoria"));}
  verify(entries,times(2)).filtered(eq(owner),any(),any(),any(),any(),any(),any(),any(),any(Pageable.class));
  verifyNoMoreInteractions(entries);
 }
 private Entry entry(UUID user,String description){return new Entry(user,"EXPENSE",description,"Categoria",new BigDecimal("1.25"),LocalDate.of(2026,11,5));}
 private int countOccurrences(String text,String needle){return (text.length()-text.replace(needle,"").length())/needle.length();}
}
