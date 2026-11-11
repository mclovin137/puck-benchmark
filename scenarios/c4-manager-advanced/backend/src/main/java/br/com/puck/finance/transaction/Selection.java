package br.com.puck.finance.transaction;
import br.com.puck.finance.common.ApiError;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.data.domain.*;
import java.math.BigDecimal;
import java.time.*;
import java.time.format.*;
import java.util.*;
import jakarta.persistence.criteria.Predicate;
public record Selection(Specification<Movement> predicate,Sort sort,int page,int size) {
 public static Selection from(UUID owner,Map<String,String> q){
  try{
   int page=Integer.parseInt(q.getOrDefault("page","0")),size=Integer.parseInt(q.getOrDefault("size","20"));
   if(page<0||size<1||size>100||page>Integer.MAX_VALUE/size)throw ApiError.invalid("Página ou tamanho inválido.");
   String sort=q.getOrDefault("sort","date,desc");if(!Set.of("date,asc","date,desc","amount,asc","amount,desc").contains(sort))throw ApiError.invalid("Ordenação inválida.");
   String[] order=sort.split(",");
   Movement.Type type=q.containsKey("type")?Movement.Type.valueOf(q.get("type")):null;
   String category=q.containsKey("category")?FinancialRules.text(q.get("category"),80):null;
   String description=q.containsKey("description")?FinancialRules.text(q.get("description"),255).toLowerCase(Locale.ROOT):null;
   LocalDate start=date(q.get("startDate")),end=date(q.get("endDate"));
   BigDecimal min=bound(q.get("minAmount")),max=bound(q.get("maxAmount"));
   if(start!=null&&end!=null&&start.isAfter(end)||min!=null&&max!=null&&min.compareTo(max)>0)throw ApiError.invalid("Intervalo invertido.");
   Specification<Movement> spec=(r,c,b)->{
    List<Predicate> all=new ArrayList<>();all.add(b.equal(r.get("ownerId"),owner));
    if(type!=null)all.add(b.equal(r.get("type"),type));if(category!=null)all.add(b.equal(r.get("category"),category));
    if(description!=null)all.add(b.like(b.lower(r.get("description")),"%"+description.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")+"%",'\\'));
    if(start!=null)all.add(b.greaterThanOrEqualTo(r.get("date"),start));if(end!=null)all.add(b.lessThanOrEqualTo(r.get("date"),end));
    if(min!=null)all.add(b.greaterThanOrEqualTo(r.get("amount"),min));if(max!=null)all.add(b.lessThanOrEqualTo(r.get("amount"),max));
    return b.and(all.toArray(Predicate[]::new));
   };
   return new Selection(spec,Sort.by(Sort.Direction.fromString(order[1]),order[0]).and(Sort.by("id")),page,size);
  }catch(IllegalArgumentException|DateTimeException e){throw ApiError.invalid("Filtro inválido.");}
 }
 private static LocalDate date(String s){if(s==null)return null;if(!s.matches("[0-9]{4}-[0-9]{2}-[0-9]{2}"))throw ApiError.invalid("Data inválida.");return LocalDate.parse(s,DateTimeFormatter.ISO_LOCAL_DATE);}
 private static BigDecimal bound(String s){if(s==null)return null;if(!s.matches("[0-9]{1,14}(\\.[0-9]{1,2})?"))throw ApiError.invalid("Faixa de valor inválida.");return new BigDecimal(s);}
}
