package br.com.puck.finance.auth.service;

import java.security.*;
import java.util.*;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.springframework.stereotype.Service;

@Service
public class PasswordService {
  private final SecureRandom random = new SecureRandom();

  public String hash(String password) {
    var salt = new byte[16];
    random.nextBytes(salt);
    return "pbkdf2-sha256$600000$"
        + Base64.getEncoder().encodeToString(salt)
        + "$"
        + Base64.getEncoder().encodeToString(derive(password, salt));
  }

  public boolean matches(String password, String hash) {
    var parts = hash.split("\\$");
    if (parts.length != 4 || !parts[0].equals("pbkdf2-sha256") || !parts[1].equals("600000"))
      return false;
    return MessageDigest.isEqual(
        derive(password, Base64.getDecoder().decode(parts[2])),
        Base64.getDecoder().decode(parts[3]));
  }

  private byte[] derive(String password, byte[] salt) {
    var spec = new PBEKeySpec(password.toCharArray(), salt, 600000, 256);
    try {
      return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
    } catch (GeneralSecurityException e) {
      throw new IllegalStateException("Hash indisponível", e);
    } finally {
      spec.clearPassword();
    }
  }
}
