package br.com.puck.finance;

import br.com.puck.finance.Models.*;
import jakarta.servlet.*;import jakarta.servlet.http.*;import org.springframework.stereotype.*;import org.springframework.web.filter.OncePerRequestFilter;import org.springframework.http.*;import org.springframework.web.bind.annotation.*;import org.springframework.security.crypto.password.PasswordEncoder;import org.springframework.transaction.annotation.Transactional;import java.io.*;import java.nio.charset.StandardCharsets;import java.security.*;import java.time.*;import java.util.*;import java.util.regex.*;

@Component class Identity { private final ThreadLocal<UUID> current=new ThreadLocal<>(); UUID get(){return current.get();} void set(UUID id){current.set(id);} void clear(){current.remove();} }
@Component class BearerFilter extends OncePerRequestFilter {
 private final Tokens tokens; private final Identity identity; BearerFilter(Tokens t,Identity i){tokens=t;identity=i;}
 protected void doFilterInternal(HttpServletRequest req,HttpServletResponse res,FilterChain chain)throws ServletException,IOException {String a=req.getHeader("Authorization"); if(a!=null&&a.startsWith("Bearer ")){String hash=AuthService.sha(a.substring(7));tokens.active(hash,OffsetDateTime.now(ZoneOffset.UTC)).ifPresent(t->identity.set(t.userId));} try{chain.doFilter(req,res);}finally{identity.clear();}}
}
@Service class AuthService {
 private final Users users;private final Tokens tokens;private final PasswordEncoder encoder; AuthService(Users u,Tokens t,PasswordEncoder e){users=u;tokens=t;encoder=e;}
 record UserDto(String id,String name,String email){} record LoginDto(String token){} record Credentials(String email,String password){} record Registration(String name,String email,String password){}
 static String sha(String s){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
 @Transactional UserDto register(Registration r){if(r==null||r.name()==null||r.email()==null||r.password()==null)throw new ApiError(HttpStatus.BAD_REQUEST,"Dados de cadastro inválidos.");String name=trim(r.name()),email=trim(r.email()).toLowerCase(Locale.ROOT),pass=r.password();if(name.isEmpty()||name.length()>120||email.isEmpty()||email.length()>254||!email.matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")||pass.length()<12||pass.length()>128)throw new ApiError(HttpStatus.BAD_REQUEST,"Dados de cadastro inválidos.");if(users.findByEmail(email).isPresent())throw new ApiError(HttpStatus.CONFLICT,"E-mail já cadastrado.");User u=users.save(new User(name,email,encoder.encode(pass)));return dto(u);}
 @Transactional LoginDto login(Credentials c){if(c==null||c.email()==null||c.password()==null)throw new ApiError(HttpStatus.BAD_REQUEST,"Credenciais inválidas.");String email=trim(c.email()).toLowerCase(Locale.ROOT);User u=users.findByEmail(email).orElseThrow(()->new ApiError(HttpStatus.UNAUTHORIZED,"E-mail ou senha inválidos."));if(!encoder.matches(c.password(),u.passwordHash))throw new ApiError(HttpStatus.UNAUTHORIZED,"E-mail ou senha inválidos.");byte[] random=new byte[32];new SecureRandom().nextBytes(random);String raw=Base64.getUrlEncoder().withoutPadding().encodeToString(random);tokens.save(new Token(sha(raw),u.id,OffsetDateTime.now(ZoneOffset.UTC).plusHours(12)));return new LoginDto(raw);}
 @Transactional void logout(String raw){if(raw!=null)tokens.active(sha(raw),OffsetDateTime.now(ZoneOffset.UTC)).ifPresent(t->{t.revokedAt=OffsetDateTime.now(ZoneOffset.UTC);tokens.save(t);});}
 UserDto me(UUID id){return dto(users.findById(id).orElseThrow(()->new ApiError(HttpStatus.UNAUTHORIZED,"Sessão inválida.")));}
 private UserDto dto(User u){return new UserDto(u.id.toString(),u.name,u.email);}static String trim(String s){return s==null?"":s.trim();}
}
@RestController @RequestMapping("/api/auth") class AuthController {
 private final AuthService service;private final Identity identity;AuthController(AuthService s,Identity i){service=s;identity=i;}
 @PostMapping("/register") ResponseEntity<?> register(@RequestBody(required=false) AuthService.Registration r){if(r==null)return ResponseEntity.badRequest().body(Map.of("message","Dados de cadastro inválidos."));return ResponseEntity.status(201).body(service.register(r));}
 @PostMapping("/login") Object login(@RequestBody(required=false) AuthService.Credentials c){if(c==null||c.email()==null||c.password()==null)return ResponseEntity.badRequest().body(Map.of("message","Credenciais inválidas."));return service.login(c);}
 @PostMapping("/logout") ResponseEntity<Void> logout(@RequestHeader(value="Authorization",required=false)String a){service.logout(a!=null&&a.startsWith("Bearer ")?a.substring(7):null);return ResponseEntity.noContent().build();}
 @GetMapping("/me") Object me(){UUID id=identity.get();if(id==null)throw new ApiError(HttpStatus.UNAUTHORIZED,"Autenticação necessária.");return service.me(id);}
}
@ResponseStatus(HttpStatus.BAD_REQUEST) class ApiError extends RuntimeException {final HttpStatus status;ApiError(HttpStatus s,String m){super(m);status=s;}}
@RestControllerAdvice class Errors { @ExceptionHandler(ApiError.class) ResponseEntity<?> api(ApiError e){return ResponseEntity.status(e.status).contentType(MediaType.APPLICATION_JSON).body(Map.of("message",e.getMessage()));} @ExceptionHandler(org.springframework.dao.DataIntegrityViolationException.class) ResponseEntity<?> conflict(){return ResponseEntity.status(409).body(Map.of("message","E-mail já cadastrado."));} @ExceptionHandler(org.springframework.http.converter.HttpMessageNotReadableException.class) ResponseEntity<?> invalid(){return ResponseEntity.badRequest().body(Map.of("message","Formato de requisição inválido."));} }

@Component class AuthRateLimitFilter extends OncePerRequestFilter {
 private final AuthRateLimiter limiter=new AuthRateLimiter(4096,60_000);
 private static final org.springframework.web.util.pattern.PathPattern LOGIN=org.springframework.web.util.pattern.PathPatternParser.defaultInstance.parse("/api/auth/login"), REGISTER=org.springframework.web.util.pattern.PathPatternParser.defaultInstance.parse("/api/auth/register");
 protected void doFilterInternal(HttpServletRequest req,HttpServletResponse res,FilterChain chain)throws ServletException,IOException {org.springframework.http.server.PathContainer requestPath;try{requestPath=org.springframework.http.server.RequestPath.parse(req.getRequestURI(),req.getContextPath()).pathWithinApplication();}catch(IllegalArgumentException ex){res.sendError(400);return;}String path=LOGIN.matches(requestPath)?"/api/auth/login":REGISTER.matches(requestPath)?"/api/auth/register":"";int limit=path.equals("/api/auth/login")?20:path.equals("/api/auth/register")?8:Integer.MAX_VALUE;if(limit==Integer.MAX_VALUE||!req.getMethod().equals("POST")){chain.doFilter(req,res);return;}String key=path+"|"+req.getRemoteAddr();if(!limiter.allow(key,System.currentTimeMillis(),limit)){res.setStatus(429);res.setContentType("application/json");res.getWriter().write("{\"message\":\"Muitas tentativas. Tente novamente mais tarde.\"}");return;}chain.doFilter(req,res);}
}
final class AuthRateLimiter {
 private record Bucket(long expiresAt,int count){} private final int capacity;private final long ttl;private final Map<String,Bucket> buckets=new HashMap<>();
 AuthRateLimiter(int capacity,long ttl){this.capacity=capacity;this.ttl=ttl;}
 synchronized boolean allow(String key,long now,int limit){buckets.entrySet().removeIf(e->e.getValue().expiresAt()<=now);Bucket b=buckets.get(key);if(b==null){if(buckets.size()>=capacity)return false;b=new Bucket(now+ttl,0);}if(b.count()>=limit)return false;buckets.put(key,new Bucket(b.expiresAt(),b.count()+1));return true;}
 synchronized int size(){return buckets.size();}
}
