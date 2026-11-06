package br.com.puck.finance.comum;

import java.util.Map;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.*;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class ApiErrors {
  public static class Unauthorized extends RuntimeException {}

  public static class NotFound extends RuntimeException {}

  public static class Conflict extends RuntimeException {}

  @ExceptionHandler({
    IllegalArgumentException.class,
    java.time.DateTimeException.class,
    MethodArgumentNotValidException.class,
    HttpMessageNotReadableException.class,
    MethodArgumentTypeMismatchException.class,
    org.springframework.web.bind.MissingServletRequestParameterException.class
  })
  ResponseEntity<?> invalid(Exception ex) {
    return response(400, "Dados inválidos");
  }

  @ExceptionHandler(Unauthorized.class)
  ResponseEntity<?> unauthorized() {
    return response(401, "Autenticação necessária");
  }

  @ExceptionHandler(NotFound.class)
  ResponseEntity<?> missing() {
    return response(404, "Registro não encontrado");
  }

  @ExceptionHandler({Conflict.class, DataIntegrityViolationException.class})
  ResponseEntity<?> conflict() {
    return response(409, "Conflito de dados");
  }

  private ResponseEntity<?> response(int status, String message) {
    return ResponseEntity.status(status).body(Map.of("message", message));
  }
}
