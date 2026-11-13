package br.com.puck.finance.transaction;
import org.springframework.data.jpa.repository.*;
import java.util.*;
public interface MovementDAO extends JpaRepository<Movement,UUID>,JpaSpecificationExecutor<Movement> { Optional<Movement> findByIdAndOwnerId(UUID id,UUID ownerId); }
