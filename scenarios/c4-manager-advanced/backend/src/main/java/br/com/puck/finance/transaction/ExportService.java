package br.com.puck.finance.transaction;
import org.springframework.stereotype.Service;
import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.pdmodel.font.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.ss.usermodel.*;
import java.io.*;
import java.util.*;
@Service
public class ExportService {
 public byte[] xlsx(List<TransactionDTO.Row> rows)throws IOException{
  try(var book=new XSSFWorkbook();var out=new ByteArrayOutputStream()){
   var sheet=book.createSheet("Movimentacoes");var head=sheet.createRow(0);String[] headers={"Data","Tipo","Descrição","Categoria","Valor"};for(int i=0;i<headers.length;i++)head.createCell(i).setCellValue(headers[i]);
   var money=book.createCellStyle();money.setDataFormat(book.createDataFormat().getFormat("#,##0.00"));
   int n=1;for(var m:rows){var row=sheet.createRow(n++);row.createCell(0).setCellValue(m.date().toString());row.createCell(1).setCellValue(m.type().name());row.createCell(2).setCellValue(m.description());row.createCell(3).setCellValue(m.category());row.createCell(4).setCellValue(m.amount());}
   var s=TransactionActor.total(rows);for(String[] item:new String[][]{{"Entradas",s.income()},{"Saídas",s.expense()},{"Saldo",s.balance()},{"Registros",Long.toString(s.count())}}){var r=sheet.createRow(n++);r.createCell(3).setCellValue(item[0]);r.createCell(4).setCellValue(item[1]);}
   sheet.createFreezePane(0,1);for(int i=0;i<5;i++)sheet.setColumnWidth(i,(i==2?42:22)*256);book.write(out);return out.toByteArray();
  }
 }
 private List<String> wrapped(String value,PDFont font)throws IOException{
  List<String> result=new ArrayList<>();StringBuilder line=new StringBuilder();
  for(int code:value.codePoints().toArray()){
   String ch=Character.isISOControl(code)?" ":new String(Character.toChars(code));
   try{font.encode(ch);}catch(IllegalArgumentException e){ch="[U+"+Integer.toHexString(code).toUpperCase(Locale.ROOT)+"]";}
   if(font.getStringWidth(line+ch)/1000*10>530){result.add(line.toString());line.setLength(0);}line.append(ch);
  }result.add(line.toString());return result;
 }
 public byte[] pdf(List<TransactionDTO.Row> rows)throws IOException{
  try(var doc=new PDDocument();var out=new ByteArrayOutputStream()){
   List<String> lines=new ArrayList<>();lines.add("Movimentações financeiras");lines.add("Data | Tipo | Descrição | Categoria | Valor");
   for(var r:rows){String line=r.date()+" | "+r.type()+" | "+r.description()+" | "+r.category()+" | "+r.amount();lines.add(line);}
   var total=TransactionActor.total(rows);lines.add("Entradas: "+total.income());lines.add("Saídas: "+total.expense());lines.add("Saldo: "+total.balance());lines.add("Registros: "+total.count());
   var font=PDType0Font.load(doc,Objects.requireNonNull(getClass().getResourceAsStream("/fonts/DejaVuSans.ttf")));
   List<String> wrappedLines=new ArrayList<>();for(String line:lines)wrappedLines.addAll(wrapped(line,font));lines=wrappedLines;
   for(int first=0;first<lines.size();first+=48){var page=new PDPage();doc.addPage(page);try(var stream=new PDPageContentStream(doc,page)){stream.beginText();stream.setFont(font,10);stream.setLeading(15);stream.newLineAtOffset(32,750);for(int i=first;i<Math.min(first+48,lines.size());i++){stream.showText(lines.get(i));stream.newLine();}stream.endText();}}
   doc.save(out);return out.toByteArray();
  }
 }
}
