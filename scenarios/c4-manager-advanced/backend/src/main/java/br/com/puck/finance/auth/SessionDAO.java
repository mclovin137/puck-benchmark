package br.com.puck.finance.auth;
import org.springframework.data.jpa.repository.JpaRepository;
public interface SessionDAO extends JpaRepository<Session,String> {}
