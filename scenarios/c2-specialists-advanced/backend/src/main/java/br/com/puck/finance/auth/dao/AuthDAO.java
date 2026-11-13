package br.com.puck.finance.auth.dao;

import br.com.puck.finance.auth.dominio.*;
import jakarta.persistence.*;
import java.time.Instant;
import java.util.*;
import org.springframework.stereotype.Repository;

@Repository
public class AuthDAO {
  @PersistenceContext private EntityManager em;

  public Optional<AuthUser> byEmail(String email) {
    return em.createQuery("select u from AuthUser u where u.email=:email", AuthUser.class)
        .setParameter("email", email)
        .getResultStream()
        .findFirst();
  }

  public Optional<AuthUser> byId(UUID id) {
    return Optional.ofNullable(em.find(AuthUser.class, id));
  }

  public void add(AuthUser user) {
    em.persist(user);
    em.flush();
  }

  public void add(AuthSession session) {
    em.persist(session);
  }

  public Optional<AuthSession> active(String hash) {
    return em.createQuery(
            "select s from AuthSession s where s.tokenHash=:hash and s.revokedAt is null and"
                + " s.expiresAt>:now",
            AuthSession.class)
        .setParameter("hash", hash)
        .setParameter("now", Instant.now())
        .getResultStream()
        .findFirst();
  }

  public void revoke(UUID sessionId) {
    em.createQuery(
            "update AuthSession s set s.revokedAt=:now where s.id=:id and s.revokedAt is null")
        .setParameter("now", Instant.now())
        .setParameter("id", sessionId)
        .executeUpdate();
  }
}
