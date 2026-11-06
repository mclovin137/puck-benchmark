package br.com.puck.finance.transaction.service;

import br.com.puck.finance.transaction.dto.TransactionDtos.*;
import java.io.*;
import java.util.*;
import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType0Font;
import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.ss.usermodel.VerticalAlignment;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Service;

@Service
public class ExportService {
  public byte[] pdf(List<Row> rows, Summary totals) {
    try (var document = new PDDocument();
        var fontStream = getClass().getResourceAsStream("/fonts/DejaVuSans.ttf");
        var output = new ByteArrayOutputStream()) {
      var font = PDType0Font.load(document, Objects.requireNonNull(fontStream));
      try (var writer = new PdfLines(document, font)) {
        for (var row : rows) {
          writer.line(row.date() + " | " + row.type() + " | " + row.amount());
          writer.line("Descrição: " + row.description());
          writer.line("Categoria: " + row.category());
          writer.line(" ");
        }
        writer.line("Entradas: " + totals.income());
        writer.line("Saídas: " + totals.expense());
        writer.line("Saldo: " + totals.balance());
        writer.line("Quantidade: " + totals.count());
      }
      document.save(output);
      return output.toByteArray();
    } catch (IOException e) {
      throw new IllegalStateException("Falha ao gerar PDF", e);
    }
  }

  public byte[] xlsx(List<Row> rows, Summary totals) {
    try (var workbook = new XSSFWorkbook();
        var output = new ByteArrayOutputStream()) {
      var sheet = workbook.createSheet("Movimentações");
      var heading = workbook.createCellStyle();
      var font = workbook.createFont();
      font.setBold(true);
      heading.setFont(font);
      var text = workbook.createCellStyle();
      text.setWrapText(true);
      text.setVerticalAlignment(VerticalAlignment.TOP);
      String[] headers = {"Data", "Tipo", "Descrição", "Categoria", "Valor"};
      var head = sheet.createRow(0);
      for (int col = 0; col < headers.length; col++) {
        var cell = head.createCell(col, CellType.STRING);
        cell.setCellValue(headers[col]);
        cell.setCellStyle(heading);
      }
      int index = 1;
      for (var row : rows) {
        var line = sheet.createRow(index++);
        String[] cells = {
          row.date().toString(), row.type().name(), row.description(), row.category(), row.amount()
        };
        for (int col = 0; col < cells.length; col++) {
          var cell = line.createCell(col, CellType.STRING);
          cell.setCellValue(cells[col]);
          cell.setCellStyle(text);
        }
        line.setHeightInPoints(Math.max(30, 15 * (1 + row.description().length() / 45)));
      }
      String[][] totalRows = {
        {"Entradas", totals.income()},
        {"Saídas", totals.expense()},
        {"Saldo", totals.balance()},
        {"Quantidade", Long.toString(totals.count())}
      };
      for (var item : totalRows) {
        var row = sheet.createRow(index++);
        row.createCell(0, CellType.STRING).setCellValue(item[0]);
        row.createCell(4, CellType.STRING).setCellValue(item[1]);
      }
      int[] widths = {13, 14, 52, 30, 24};
      for (int col = 0; col < widths.length; col++) sheet.setColumnWidth(col, widths[col] * 256);
      sheet.createFreezePane(0, 1);
      sheet.setRepeatingRows(new org.apache.poi.ss.util.CellRangeAddress(0, 0, -1, -1));
      workbook.write(output);
      return output.toByteArray();
    } catch (IOException e) {
      throw new IllegalStateException("Falha ao gerar XLSX", e);
    }
  }

  private static final class PdfLines implements AutoCloseable {
    private final PDDocument document;
    private final PDType0Font font;
    private PDPageContentStream stream;
    private float y;

    PdfLines(PDDocument document, PDType0Font font) throws IOException {
      this.document = document;
      this.font = font;
      page();
    }

    private void page() throws IOException {
      if (stream != null) stream.close();
      var page = new PDPage(PDRectangle.A4);
      document.addPage(page);
      stream = new PDPageContentStream(document, page);
      y = 800;
      draw("Movimentações financeiras — Data | Tipo | Valor");
      draw("Página " + document.getNumberOfPages());
      y -= 12;
    }

    void line(String source) throws IOException {
      // Glyphs absent from the bundled font are represented explicitly, never silently dropped.
      var safe = new StringBuilder();
      for (int offset = 0; offset < source.length(); ) {
        int cp = source.codePointAt(offset);
        offset += Character.charCount(cp);
        String value = new String(Character.toChars(cp));
        try {
          font.encode(value);
          safe.append(value);
        } catch (IllegalArgumentException ex) {
          safe.append("[U+").append(Integer.toHexString(cp).toUpperCase(Locale.ROOT)).append("]");
        }
      }
      var part = new StringBuilder();
      for (int offset = 0; offset < safe.length(); ) {
        int cp = safe.codePointAt(offset);
        offset += Character.charCount(cp);
        String next = new String(Character.toChars(cp));
        if (font.getStringWidth(part + next) / 1000 * 10 > 510) {
          if (y < 45) page();
          draw(part.toString());
          part.setLength(0);
        }
        part.append(next);
      }
      if (!part.isEmpty()) {
        if (y < 45) page();
        draw(part.toString());
      }
    }

    private void draw(String text) throws IOException {
      stream.beginText();
      stream.setFont(font, 10);
      stream.newLineAtOffset(40, y);
      stream.showText(text);
      stream.endText();
      y -= 15;
    }

    @Override
    public void close() throws IOException {
      if (stream != null) stream.close();
    }
  }
}
