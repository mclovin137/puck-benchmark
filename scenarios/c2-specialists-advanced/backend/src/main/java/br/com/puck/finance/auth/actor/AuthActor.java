package br.com.puck.finance.auth.actor;

import br.com.puck.finance.auth.dao.AuthDAO;
import br.com.puck.finance.auth.dominio.*;
import br.com.puck.finance.auth.dto.AuthDtos.*;
import br.com.puck.finance.auth.service.PasswordService;
import br.com.puck.finance.comum.ApiErrors.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthActor {
  private final AuthDAO dao;
  private final PasswordService passwords;
  private final SecureRandom random = new SecureRandom();
  private final String dummyHash;

  public record Principal(UUID userId, UUID sessionId) {}

  public AuthActor(AuthDAO dao, PasswordService passwords) {
    this.dao = dao;
    this.passwords = passwords;
    dummyHash = passwords.hash("dummy-password-that-is-never-used");
  }

  @Transactional
  public User register(Register input) {
    var email = email(input.email());
    var name = input.name().trim();
    if (name.isEmpty() || name.length() > 120) throw new IllegalArgumentException();
    if (dao.byEmail(email).isPresent()) throw new Conflict();
    var user = new AuthUser(name, email, passwords.hash(input.password()));
    dao.add(user);
    return dto(user);
  }

  @Transactional
  public Token login(Login input) {
    var user = dao.byEmail(email(input.email()));
    boolean valid =
        passwords.matches(input.password(), user.map(u -> u.passwordHash).orElse(dummyHash));
    if (user.isEmpty() || !valid) throw new Unauthorized();
    var bytes = new byte[32];
    random.nextBytes(bytes);
    var token = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    dao.add(new AuthSession(user.get().id, digest(token)));
    return new Token(token);
  }

  @Transactional(readOnly = true)
  public Principal authenticate(String token) {
    if (token == null || !token.matches("[A-Za-z0-9_-]{43}")) throw new Unauthorized();
    var session = dao.active(digest(token)).orElseThrow(Unauthorized::new);
    return new Principal(session.userId, session.id);
  }

  @Transactional(readOnly = true)
  public User me(Principal principal) {
    return dto(dao.byId(principal.userId()).orElseThrow(Unauthorized::new));
  }

  @Transactional
  public void logout(Principal principal) {
    dao.revoke(principal.sessionId());
  }

  private User dto(AuthUser user) {
    return new User(user.id, user.name, user.email);
  }

  private String email(String raw) {
    var value = raw.trim().toLowerCase(Locale.ROOT);
    if (value.length() > 254 || !value.matches("[^\\s@]+@[^\\s@]+\\.[^\\s@]+"))
      throw new IllegalArgumentException();
    return value;
  }

  private String digest(String token) {
    try {
      return HexFormat.of()
          .formatHex(
              MessageDigest.getInstance("SHA-256")
                  .digest(token.getBytes(StandardCharsets.US_ASCII)));
    } catch (NoSuchAlgorithmException ex) {
      throw new IllegalStateException(ex);
    }
  }
}
