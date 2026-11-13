package br.com.puck.finance.transaction;
import br.com.puck.finance.common.ApiError;
import java.math.BigDecimal;
public final class FinancialRules {
 private FinancialRules(){}
 public static BigDecimal amount(String raw){
  if(raw==null||!raw.matches("[0-9]{1,14}(\\.[0-9]{1,2})?"))throw ApiError.invalid("Valor deve ter até 14 inteiros e 2 decimais.");
  BigDecimal n=new BigDecimal(raw).setScale(2);if(n.signum()<=0)throw ApiError.invalid("Valor deve ser maior que zero.");return n;
 }
 public static String text(String raw,int max){if(raw==null||raw.strip().isEmpty()||raw.strip().length()>max)throw ApiError.invalid("Texto obrigatório ou muito longo.");return raw.strip();}
}
