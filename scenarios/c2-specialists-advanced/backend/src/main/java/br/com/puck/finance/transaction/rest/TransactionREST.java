package br.com.puck.finance.transaction.rest;

import br.com.puck.finance.auth.actor.AuthActor.Principal;
import br.com.puck.finance.transaction.actor.TransactionActor;
import br.com.puck.finance.transaction.dto.TransactionDtos.*;
import br.com.puck.finance.transaction.service.TransactionRules;
import jakarta.validation.Valid;
import java.util.*;
import org.springframework.http.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/transactions")
public class TransactionREST {
  private final TransactionActor actor;

  public TransactionREST(TransactionActor actor) {
    this.actor = actor;
  }

  @PostMapping
  @ResponseStatus(HttpStatus.CREATED)
  public Row create(@AuthenticationPrincipal Principal p, @Valid @RequestBody Write input) {
    return actor.create(p.userId(), input);
  }

  @GetMapping
  public Page list(@AuthenticationPrincipal Principal p, @RequestParam Map<String, String> query) {
    return actor.list(p.userId(), TransactionRules.filter(query));
  }

  @GetMapping("/{id}")
  public Row get(@AuthenticationPrincipal Principal p, @PathVariable UUID id) {
    return actor.get(p.userId(), id);
  }

  @PutMapping("/{id}")
  public Row update(
      @AuthenticationPrincipal Principal p,
      @PathVariable UUID id,
      @Valid @RequestBody Write input) {
    return actor.update(p.userId(), id, input);
  }

  @DeleteMapping("/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void delete(@AuthenticationPrincipal Principal p, @PathVariable UUID id) {
    actor.delete(p.userId(), id);
  }

  @GetMapping("/summary")
  public Summary summary(
      @AuthenticationPrincipal Principal p, @RequestParam Map<String, String> query) {
    return actor.summary(p.userId(), TransactionRules.filter(query));
  }

  @GetMapping("/export.pdf")
  public ResponseEntity<byte[]> pdf(
      @AuthenticationPrincipal Principal p, @RequestParam Map<String, String> query) {
    return export(p, query, true);
  }

  @GetMapping("/export.xlsx")
  public ResponseEntity<byte[]> xlsx(
      @AuthenticationPrincipal Principal p, @RequestParam Map<String, String> query) {
    return export(p, query, false);
  }

  private ResponseEntity<byte[]> export(Principal p, Map<String, String> query, boolean pdf) {
    return ResponseEntity.ok()
        .header(
            HttpHeaders.CONTENT_DISPOSITION,
            "attachment; filename=movimentacoes." + (pdf ? "pdf" : "xlsx"))
        .contentType(
            MediaType.parseMediaType(
                pdf
                    ? "application/pdf"
                    : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
        .body(actor.export(p.userId(), TransactionRules.filter(query), pdf));
  }
}
