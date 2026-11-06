package br.com.puck.finance;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class ExportAsyncResponseTest {
 @Test void capacityErrorIs429OnAsyncDispatch() throws Exception {
  TransactionService service=mock(TransactionService.class);
  when(service.export(anyMap(),eq(false))).thenReturn(output->{throw new ApiError(HttpStatus.TOO_MANY_REQUESTS,"Há exportações em andamento.");});
  MockMvc mvc=MockMvcBuilders.standaloneSetup(new TransactionController(service)).setControllerAdvice(new Errors()).build();
  var initial=mvc.perform(get("/api/transactions/export.pdf")).andExpect(request().asyncStarted()).andReturn();
  mvc.perform(asyncDispatch(initial)).andExpect(status().isTooManyRequests());
 }
}
