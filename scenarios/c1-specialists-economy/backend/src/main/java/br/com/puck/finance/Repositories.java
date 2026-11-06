package br.com.puck.finance;

import br.com.puck.finance.Models.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import java.util.*;
import java.time.*;
import java.math.BigDecimal;

interface Users extends JpaRepository<User,UUID> { Optional<User> findByEmail(String email); }
interface Tokens extends JpaRepository<Token,String> { @Query("select t from AuthToken t where t.tokenHash=:hash and t.revokedAt is null and t.expiresAt>:now") Optional<Token> active(@Param("hash") String hash,@Param("now") OffsetDateTime now); }
interface Entries extends JpaRepository<Entry,UUID> {
 @Query(value="select e from TransactionEntry e where e.userId=:uid and (:type is null or e.type=:type) and (:category is null or e.category=:category) and (lower(e.description) like concat('%',lower(cast(:description as string)),'%') escape '!') and (cast(:startDate as date) is null or e.date>=:startDate) and (cast(:endDate as date) is null or e.date<=:endDate) and (:minAmount is null or e.amount>=:minAmount) and (:maxAmount is null or e.amount<=:maxAmount)", countQuery="select count(e) from TransactionEntry e where e.userId=:uid and (:type is null or e.type=:type) and (:category is null or e.category=:category) and (lower(e.description) like concat('%',lower(cast(:description as string)),'%') escape '!') and (cast(:startDate as date) is null or e.date>=:startDate) and (cast(:endDate as date) is null or e.date<=:endDate) and (:minAmount is null or e.amount>=:minAmount) and (:maxAmount is null or e.amount<=:maxAmount)")
 org.springframework.data.domain.Page<Entry> filtered(@Param("uid") UUID uid,@Param("type") String type,@Param("category") String category,@Param("description") String description,@Param("startDate") LocalDate start,@Param("endDate") LocalDate end,@Param("minAmount") BigDecimal min,@Param("maxAmount") BigDecimal max,org.springframework.data.domain.Pageable pageable);
 @Query("select e from TransactionEntry e where e.userId=:uid and e.id=:id") Optional<Entry> owned(@Param("uid") UUID uid,@Param("id") UUID id);
}
