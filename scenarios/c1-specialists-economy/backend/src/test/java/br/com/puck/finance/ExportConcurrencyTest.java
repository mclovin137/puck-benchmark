package br.com.puck.finance;

import org.junit.jupiter.api.Test;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import java.io.ByteArrayOutputStream;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class ExportConcurrencyTest {
 @Test void callbacksNeverStartedDoNotOccupySlots() throws Exception {
  Identity identity=mock(Identity.class); when(identity.get()).thenReturn(UUID.randomUUID());
  Entries entries=mock(Entries.class);
  when(entries.filtered(any(),any(),any(),any(),any(),any(),any(),any(),any(Pageable.class))).thenAnswer(c->new PageImpl<>(List.of()));
  TransactionService service=new TransactionService(entries,identity);
  service.export(Map.of(),false); service.export(Map.of(),false);
  service.export(Map.of(),false).writeTo(new ByteArrayOutputStream());
 }
 @Test void twoActiveExportsLimitThirdAndReleaseSlots() throws Exception {
  Identity identity=mock(Identity.class); when(identity.get()).thenReturn(UUID.randomUUID());
  Entries entries=mock(Entries.class); CountDownLatch started=new CountDownLatch(2), release=new CountDownLatch(1);
  when(entries.filtered(any(),any(),any(),any(),any(),any(),any(),any(),any(Pageable.class))).thenAnswer(c->{started.countDown(); if(!release.await(5,TimeUnit.SECONDS)) throw new IllegalStateException("timeout"); return new PageImpl<>(List.of());});
  TransactionService service=new TransactionService(entries,identity);
  var first=service.export(Map.of(),false); var second=service.export(Map.of(),false); var third=service.export(Map.of(),false);
  ExecutorService executor=Executors.newFixedThreadPool(2);
  try {
   Future<?> a=executor.submit(()->{try{first.writeTo(new ByteArrayOutputStream());}catch(Exception e){throw new RuntimeException(e);}});
   Future<?> b=executor.submit(()->{try{second.writeTo(new ByteArrayOutputStream());}catch(Exception e){throw new RuntimeException(e);}});
   assertTrue(started.await(5,TimeUnit.SECONDS));
   assertThrows(ApiError.class,()->third.writeTo(new ByteArrayOutputStream()));
   release.countDown(); a.get(5,TimeUnit.SECONDS); b.get(5,TimeUnit.SECONDS);
   service.export(Map.of(),false).writeTo(new ByteArrayOutputStream());
  } finally {release.countDown();executor.shutdownNow();}
 }
}
