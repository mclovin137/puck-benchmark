package br.com.puck.finance.auth;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import java.util.*;
@RestController @RequestMapping("/api/auth")
public class AuthREST {
 private final AuthActor actor;public AuthREST(AuthActor actor){this.actor=actor;}
 @PostMapping("/register") @ResponseStatus(HttpStatus.CREATED) public AuthActor.Profile register(@Valid @RequestBody AuthActor.Register r){return actor.register(r);}
 @PostMapping("/login") public Map<String,String> login(@Valid @RequestBody AuthActor.Login r){return actor.login(r);}
 @GetMapping("/me") public AuthActor.Profile me(@AuthenticationPrincipal UUID owner){return actor.me(owner);}
 @PostMapping("/logout") @ResponseStatus(HttpStatus.NO_CONTENT) public void logout(@RequestHeader("Authorization")String h){actor.logout(h.substring(7));}
}
