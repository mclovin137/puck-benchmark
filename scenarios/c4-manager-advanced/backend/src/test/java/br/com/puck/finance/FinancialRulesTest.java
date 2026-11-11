package br.com.puck.finance;
import br.com.puck.finance.transaction.FinancialRules;
import br.com.puck.finance.common.ApiError;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class FinancialRulesTest {
 @Test void preservesMaximumAndCents(){assertEquals("99999999999999.99",FinancialRules.amount("99999999999999.99").toPlainString());assertEquals("0.10",FinancialRules.amount("0.10").toPlainString());}
 @Test void rejectsNonPositivePrecisionExponentAndOverflow(){for(String value:new String[]{"0","-1","1.001","1e3","100000000000000.00","NaN"," 1",".2"})assertThrows(ApiError.class,()->FinancialRules.amount(value),value);}
 @Test void rejectsBlankAndTrims(){assertEquals("Mercado",FinancialRules.text(" Mercado ",80));assertThrows(ApiError.class,()->FinancialRules.text("  ",80));}
}
