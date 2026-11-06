package br.com.puck.finance.auth.rest;

import br.com.puck.finance.auth.actor.AuthActor;
import br.com.puck.finance.auth.actor.AuthActor.Principal;
import br.com.puck.finance.auth.dto.AuthDtos.*;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthREST {
  private final AuthActor actor;

  public AuthREST(AuthActor actor) {
    this.actor = actor;
  }

  @PostMapping("/register")
  @ResponseStatus(HttpStatus.CREATED)
  public User register(@Valid @RequestBody Register input) {
    return actor.register(input);
  }

  @PostMapping("/login")
  public Token login(@Valid @RequestBody Login input) {
    return actor.login(input);
  }

  @GetMapping("/me")
  public User me(@AuthenticationPrincipal Principal principal) {
    return actor.me(principal);
  }

  @PostMapping("/logout")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void logout(@AuthenticationPrincipal Principal principal) {
    actor.logout(principal);
  }
}
