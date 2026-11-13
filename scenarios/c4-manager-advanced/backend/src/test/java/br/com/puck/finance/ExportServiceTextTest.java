package br.com.puck.finance;

import br.com.puck.finance.transaction.ExportService;
import br.com.puck.finance.transaction.Movement;
import br.com.puck.finance.transaction.TransactionDTO;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

class ExportServiceTextTest {
 private static TransactionDTO.Row row(String description,String amount){
  return new TransactionDTO.Row(UUID.randomUUID(),Movement.Type.INCOME,description,"Educação",amount,
    LocalDate.of(2026,10,10),Instant.EPOCH,Instant.EPOCH);
 }
 private static String compact(String value){return value.replaceAll("\\s+","");}

 // PDFTextStripper normaliza ligaturas no texto final. Inspecionar o Unicode
 // bruto dos glifos impede que essa normalização esconda a substituição de ff/ffi.
 private static final class RawText extends PDFTextStripper {
  private final StringBuilder raw=new StringBuilder();
  RawText()throws IOException{}
  @Override protected void writeString(String text,List<TextPosition> positions){
   for(var position:positions)raw.append(position.getUnicode());
   raw.append('\n');
  }
 }

 @ParameterizedTest
 @ValueSource(strings={"Texto de controle Café e educação","office affinity Café e educação",
   "coffre offshore ff ffi ação","Descrição longa office affinity educação "+
   "Descrição longa office affinity educação Descrição longa office affinity educação"})
 void preservesLiteralGlyphTextAndExactDecimal(String description)throws Exception{
  byte[] pdf=new ExportService().pdf(List.of(row(description,"12345678901234.56")));
  try(var doc=Loader.loadPDF(pdf)){
   var reader=new RawText();reader.getText(doc);String raw=compact(reader.raw.toString());
   assertTrue(raw.contains(compact(description)),()->"Texto literal não preservado: "+reader.raw);
   assertTrue(raw.contains("Educação"));
   assertTrue(raw.contains("12345678901234.56"));
   for(var page:doc.getPages())for(var name:page.getResources().getFontNames())
    assertTrue(page.getResources().getFont(name).isEmbedded());
  }
 }

 @Test void keepsLiteralTextAcrossPages()throws Exception{
  var rows=IntStream.range(0,80).mapToObj(i->row("office affinity educação item "+i,"10.00")).toList();
  try(var doc=Loader.loadPDF(new ExportService().pdf(rows))){
   assertTrue(doc.getNumberOfPages()>1);
   var reader=new RawText();reader.getText(doc);String raw=compact(reader.raw.toString());
   for(var value:rows)assertTrue(raw.contains(compact(value.description())),value.description());
   assertTrue(raw.contains("800.00"));
  }
 }
}
