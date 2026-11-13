package br.com.puck.finance.auth;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
public interface UserDAO extends JpaRepository<User,UUID> { Optional<User> findByEmail(String email); boolean existsByEmail(String email); }
