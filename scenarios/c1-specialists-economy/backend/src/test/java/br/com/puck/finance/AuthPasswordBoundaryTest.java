package br.com.puck.finance;
import org.junit.jupiter.api.Test;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
class AuthPasswordBoundaryTest {
 @Test void registerAndLoginWith128CharactersDistinguishesFinalCharacter() {
  Users users=mock(Users.class); Tokens tokens=mock(Tokens.class);
  when(users.save(any())).thenAnswer(c->c.getArgument(0));
  AuthService auth=new AuthService(users,tokens,new Application().passwordEncoder());
  String password="a".repeat(127)+"b";
  auth.register(new AuthService.Registration("Nome","test@example.com",password));
  var saved=org.mockito.ArgumentCaptor.forClass(Models.User.class);
  verify(users).save(saved.capture());
  when(users.findByEmail("test@example.com")).thenReturn(Optional.of(saved.getValue()));
  assertNotNull(auth.login(new AuthService.Credentials("test@example.com",password)).token());
  assertThrows(ApiError.class,()->auth.login(new AuthService.Credentials("test@example.com","a".repeat(128))));
 }
 @Test void supportsLegacyBcryptAndLongUtf8Passwords() {
  var encoder=new Application().passwordEncoder();
  String legacy=new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder(12).encode("senha antiga válida");
  assertTrue(encoder.matches("senha antiga válida",legacy));
  String password="á".repeat(128);
  String hash=encoder.encode(password);
  assertTrue(encoder.matches(password,hash));
  assertFalse(encoder.matches("á".repeat(127)+"a",hash));
 }
}
