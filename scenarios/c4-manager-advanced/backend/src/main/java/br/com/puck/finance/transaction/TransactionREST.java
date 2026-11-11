package br.com.puck.finance.transaction;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.http.*;
import jakarta.validation.Valid;
import java.util.*;
import java.io.IOException;
@RestController @RequestMapping("/api/transactions")
public class TransactionREST {
 private final TransactionActor actor;private final ExportService export;
 public TransactionREST(TransactionActor actor,ExportService export){this.actor=actor;this.export=export;}
 @PostMapping @ResponseStatus(HttpStatus.CREATED) public TransactionDTO.Row create(@AuthenticationPrincipal UUID owner,@Valid @RequestBody TransactionDTO.Input r){return actor.create(owner,r);}
 @GetMapping public TransactionDTO.Listing list(@AuthenticationPrincipal UUID owner,@RequestParam Map<String,String> q){return actor.list(Selection.from(owner,q));}
 @GetMapping("/{id}") public TransactionDTO.Row get(@AuthenticationPrincipal UUID owner,@PathVariable UUID id){return actor.get(owner,id);}
 @PutMapping("/{id}") public TransactionDTO.Row update(@AuthenticationPrincipal UUID owner,@PathVariable UUID id,@Valid @RequestBody TransactionDTO.Input r){return actor.update(owner,id,r);}
 @DeleteMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT) public void delete(@AuthenticationPrincipal UUID owner,@PathVariable UUID id){actor.delete(owner,id);}
 @GetMapping("/summary") public TransactionDTO.Summary summary(@AuthenticationPrincipal UUID owner,@RequestParam Map<String,String> q){return actor.summary(Selection.from(owner,q));}
 @GetMapping("/export.pdf") public ResponseEntity<byte[]> pdf(@AuthenticationPrincipal UUID owner,@RequestParam Map<String,String> q)throws IOException{return file(export.pdf(actor.rows(Selection.from(owner,q))),"application/pdf","movimentacoes.pdf");}
 @GetMapping("/export.xlsx") public ResponseEntity<byte[]> xlsx(@AuthenticationPrincipal UUID owner,@RequestParam Map<String,String> q)throws IOException{return file(export.xlsx(actor.rows(Selection.from(owner,q))),"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","movimentacoes.xlsx");}
 private ResponseEntity<byte[]> file(byte[] bytes,String type,String name){return ResponseEntity.ok().header("Content-Disposition","attachment; filename=\""+name+"\"").header("Cache-Control","no-store").contentType(MediaType.parseMediaType(type)).body(bytes);}
}
