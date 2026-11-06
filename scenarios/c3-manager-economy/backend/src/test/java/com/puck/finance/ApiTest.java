package com.puck.finance;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;
class ApiTest {
 @Test void valoresSaoDecimaisEPositivos(){assertEquals("123.40",Api.amount("123.4").toPlainString());assertThrows(Exception.class,()->Api.amount("0"));assertThrows(Exception.class,()->Api.amount("1.001"));assertThrows(Exception.class,()->Api.amount("1e3"));}
 @Test void resumoNaoUsaPontoFlutuante(){Entry a=new Entry();a.type="INCOME";a.amount=new BigDecimal("0.30");Entry b=new Entry();b.type="EXPENSE";b.amount=new BigDecimal("0.10");assertEquals(new Api.Summary("0.30","0.10","0.20",2),Api.summary(List.of(a,b)));}
 @Test void acessoConsultaProprietario(){Users u=mock(Users.class);Sessions s=mock(Sessions.class);Entries es=mock(Entries.class);Api api=new Api(u,s,es);assertThrows(Exception.class,()->api.owned(7L,2L));verify(es).findByIdAndUserId(7L,2L);}
 @Test void registroNormalizaEmail(){assertEquals("teste@example.com",Api.email(" Teste@Example.com "));}
}
