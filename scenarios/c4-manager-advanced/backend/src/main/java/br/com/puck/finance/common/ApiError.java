package br.com.puck.finance.common;
import org.springframework.http.HttpStatus;
public class ApiError extends RuntimeException {
 public final HttpStatus status;
 public ApiError(HttpStatus status,String message){super(message);this.status=status;}
 public static ApiError invalid(String message){return new ApiError(HttpStatus.BAD_REQUEST,message);}
 public static ApiError missing(){return new ApiError(HttpStatus.NOT_FOUND,"Registro não encontrado.");}
}
