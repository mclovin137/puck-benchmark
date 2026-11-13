package br.com.puck.finance;

import static org.assertj.core.api.Assertions.*;

import br.com.puck.finance.auth.service.PasswordService;
import br.com.puck.finance.transaction.service.TransactionRules;
import org.junit.jupiter.api.Test;

class DomainTest {
  @Test
  void moneyIsExactAndBounded() {
    assertThat(TransactionRules.amount("99999999999999.99").toPlainString())
        .isEqualTo("99999999999999.99");
    assertThatThrownBy(() -> TransactionRules.amount("1.001"))
        .isInstanceOf(IllegalArgumentException.class);
    assertThatThrownBy(() -> TransactionRules.amount("100000000000000.00"))
        .isInstanceOf(IllegalArgumentException.class);
    assertThatThrownBy(() -> TransactionRules.amount("0"))
        .isInstanceOf(IllegalArgumentException.class);
  }

  @Test
  void passwordIsSaltedAndNeverTruncated() {
    var service = new PasswordService();
    var password = "é".repeat(72) + "A";
    var encoded = service.hash(password);
    assertThat(service.matches(password, encoded)).isTrue();
    assertThat(service.matches("é".repeat(72) + "B", encoded)).isFalse();
    assertThat(service.hash(password)).isNotEqualTo(encoded);
  }
}
