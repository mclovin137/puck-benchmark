package br.com.puck.finance.auth;
import br.com.puck.finance.common.ApiError;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.security.crypto.password.Pbkdf2PasswordEncoder;
import org.springframework.http.HttpStatus;
import jakarta.validation.constraints.*;
import java.security.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
@Service
public class AuthActor {
 public record Register(@NotBlank @Size(max=120) String name,@NotBlank @Email @Size(max=254) String email,@NotNull @Size(min=12,max=128) String password){public Register{if(name!=null)name=name.strip();if(email!=null)email=email.strip();}}
 public record Login(@NotBlank @Email @Size(max=254) String email,@NotNull @Size(min=12,max=128) String password){public Login{if(email!=null)email=email.strip();}}
 public record Profile(UUID id,String name,String email){}
 private final UserDAO users; private final SessionDAO sessions;
 private final Pbkdf2PasswordEncoder encoder=Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8();
 private final String dummy=encoder.encode("unavailable-account-password");
 private final SecureRandom random=new SecureRandom();
 public AuthActor(UserDAO users,SessionDAO sessions){this.users=users;this.sessions=sessions;}
 private String normalized(String email){return email.strip().toLowerCase(Locale.ROOT);}
 public Profile profile(User u){return new Profile(u.id,u.name,u.email);}
 @Transactional public Profile register(Register r){
  String name=r.name().strip(),email=normalized(r.email());
  if(name.isEmpty())throw ApiError.invalid("Informe seu nome.");
  if(users.existsByEmail(email))throw new ApiError(HttpStatus.CONFLICT,"E-mail já cadastrado.");
  return profile(users.saveAndFlush(new User(name,email,encoder.encode(r.password()))));
 }
 @Transactional public Map<String,String> login(Login r){
  User u=users.findByEmail(normalized(r.email())).orElse(null);
  boolean valid=encoder.matches(r.password(),u==null?dummy:u.passwordHash);
  if(u==null||!valid)throw new ApiError(HttpStatus.UNAUTHORIZED,"E-mail ou senha inválidos.");
  byte[] bytes=new byte[32];random.nextBytes(bytes);String token=Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
  sessions.save(new Session(hash(token),u.id));return Map.of("token",token);
 }
 public Optional<UUID> authenticate(String token){return sessions.findById(hash(token)).filter(s->s.expiresAt.isAfter(java.time.Instant.now())).map(s->s.ownerId);}
 @Transactional public void logout(String token){sessions.deleteById(hash(token));}
 public Profile me(UUID owner){return users.findById(owner).map(this::profile).orElseThrow(ApiError::missing);}
 public static String hash(String token){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
}
