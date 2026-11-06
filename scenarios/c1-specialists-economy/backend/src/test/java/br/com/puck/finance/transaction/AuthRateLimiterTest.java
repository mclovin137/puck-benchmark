package br.com.puck.finance;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class AuthRateLimiterTest {
 @Test void allowsLegitimateBurstThenRejectsAbuseAndExpiresBucket(){AuthRateLimiter limiter=new AuthRateLimiter(2,1000);assertTrue(limiter.allow("ip",100,3));assertTrue(limiter.allow("ip",101,3));assertTrue(limiter.allow("ip",102,3));assertFalse(limiter.allow("ip",103,3));assertTrue(limiter.allow("ip",1100,3));}
 @Test void boundsDistinctOrigins(){AuthRateLimiter limiter=new AuthRateLimiter(2,1000);assertTrue(limiter.allow("a",1,3));assertTrue(limiter.allow("b",1,3));assertFalse(limiter.allow("c",1,3));assertEquals(2,limiter.size());}
}
