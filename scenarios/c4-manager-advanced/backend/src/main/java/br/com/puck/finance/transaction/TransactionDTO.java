package br.com.puck.finance.transaction;
import jakarta.validation.constraints.*;
import java.util.*;
import java.time.*;
public final class TransactionDTO {
 private TransactionDTO(){}
 public record Input(@NotNull Movement.Type type,@NotBlank @Size(max=255) String description,@NotBlank @Size(max=80) String category,@NotNull @com.fasterxml.jackson.databind.annotation.JsonDeserialize(using=br.com.puck.finance.common.StrictString.class) String amount,@NotNull @Pattern(regexp="[0-9]{4}-[0-9]{2}-[0-9]{2}") String date){public Input{if(description!=null)description=description.strip();if(category!=null)category=category.strip();}}
 public record Row(UUID id,Movement.Type type,String description,String category,String amount,LocalDate date,Instant createdAt,Instant updatedAt){
  public static Row from(Movement m){return new Row(m.id,m.type,m.description,m.category,m.amount.toPlainString(),m.date,m.createdAt,m.updatedAt);}
 }
 public record Listing(List<Row> content,long totalElements,int page,int size,int totalPages){}
 public record Summary(String income,String expense,String balance,long count){}
}
