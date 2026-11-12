import com.fasterxml.jackson.databind.ObjectMapper;
import com.puck.finance.App;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerMapping;
import org.springframework.web.servlet.ViewResolver;
import org.springframework.web.servlet.handler.AbstractUrlHandlerMapping;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
import org.springframework.web.servlet.view.UrlBasedViewResolver;
import org.springframework.web.servlet.view.xslt.XsltView;
import org.springframework.web.servlet.view.xslt.XsltViewResolver;

/** Probe externo de metadados. Não registra beans, chama rotas ou lê dados. */
public final class ContextProbe {
  private static Map<String,Object> resolver(ViewResolver resolver, Set<Object> visited) throws Exception {
    Map<String,Object> item = new TreeMap<>();
    item.put("class", resolver.getClass().getName());
    if (!visited.add(resolver)) { item.put("repeated", true); return item; }
    if (resolver instanceof UrlBasedViewResolver) {
      var method = UrlBasedViewResolver.class.getDeclaredMethod("getViewClass");
      method.setAccessible(true);
      Class<?> view = (Class<?>) method.invoke(resolver);
      item.put("configured_view_class", view == null ? null : view.getName());
      item.put("configured_view_is_xslt", view != null && XsltView.class.isAssignableFrom(view));
    }
    // Somente getters de lista de resolvers das classes Spring já carregadas.
    String name = resolver.getClass().getName();
    if (name.equals("org.springframework.web.servlet.view.ViewResolverComposite") ||
        name.equals("org.springframework.web.servlet.view.ContentNegotiatingViewResolver")) {
      Object value = resolver.getClass().getMethod("getViewResolvers").invoke(resolver);
      List<Object> children = new ArrayList<>();
      if (value instanceof List<?> list) for (Object child : list)
        if (child instanceof ViewResolver vr) children.add(resolver(vr, visited));
      item.put("delegates", children);
    }
    return item;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("artifact commit required");
    Path artifact = Path.of(args[0]);
    Map<String,Object> report = new TreeMap<>();
    report.put("schema_version", 1);
    report.put("scenario", "C3");
    report.put("source_commit", args[1]);
    report.put("artifact_sha256", HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(artifact))));
    report.put("java_version", System.getProperty("java.version"));
    report.put("started_at", Instant.now().toString());
    ConfigurableApplicationContext ctx = null;
    try {
      ctx = SpringApplication.run(App.class, "--server.address=127.0.0.1", "--server.port=0");
      report.put("spring_version", org.springframework.core.SpringVersion.getVersion());
      report.put("boot_version", org.springframework.boot.SpringBootVersion.getVersion());
      report.put("application_class", App.class.getName());
      report.put("active_profiles", Arrays.asList(ctx.getEnvironment().getActiveProfiles()));
      report.put("xslt_view_beans", Arrays.asList(ctx.getBeanNamesForType(XsltView.class, true, false)));
      report.put("xslt_resolver_beans", Arrays.asList(ctx.getBeanNamesForType(XsltViewResolver.class, true, false)));
      List<Object> mappings = new ArrayList<>();
      List<Object> handlers = new ArrayList<>();
      for (var entry : new TreeMap<>(ctx.getBeansOfType(HandlerMapping.class, true, false)).entrySet()) {
        HandlerMapping mapping = entry.getValue();
        Map<String,Object> row = new TreeMap<>();
        row.put("bean", entry.getKey()); row.put("class", mapping.getClass().getName());
        if (mapping instanceof AbstractUrlHandlerMapping urls) {
          Map<String,String> types = new TreeMap<>();
          urls.getHandlerMap().forEach((path,handler) -> types.put(path, handler.getClass().getName()));
          row.put("url_handler_classes", types);
        }
        mappings.add(row);
        if (mapping instanceof RequestMappingHandlerMapping requests) {
          for (var handlerEntry : requests.getHandlerMethods().entrySet()) {
            HandlerMethod method = handlerEntry.getValue();
            var info = handlerEntry.getKey();
            Map<String,Object> h = new TreeMap<>();
            h.put("controller", method.getBeanType().getName());
            h.put("method", method.getMethod().getName());
            h.put("rest_controller", method.getBeanType().isAnnotationPresent(RestController.class));
            h.put("return_type", method.getMethod().getGenericReturnType().getTypeName());
            h.put("patterns", new TreeSet<>(info.getPatternValues()));
            h.put("http_methods", info.getMethodsCondition().getMethods().stream().map(Enum::name).sorted().toList());
            h.put("produces", new TreeSet<>(info.getProducesCondition().getProducibleMediaTypes().stream().map(Object::toString).toList()));
            handlers.add(h);
          }
        }
      }
      handlers.sort(Comparator.comparing(Object::toString));
      report.put("handler_mappings", mappings);
      report.put("request_handlers", handlers);
      List<Object> resolvers = new ArrayList<>();
      for (var entry : new TreeMap<>(ctx.getBeansOfType(ViewResolver.class, true, false)).entrySet()) {
        Map<String,Object> row = resolver(entry.getValue(), Collections.newSetFromMap(new IdentityHashMap<>()));
        row.put("bean", entry.getKey()); resolvers.add(row);
      }
      report.put("view_resolvers", resolvers);
      report.put("status", "observed");
    } finally {
      if (ctx != null) { ctx.close(); report.put("context_closed", !ctx.isActive()); }
    }
    report.put("finished_at", Instant.now().toString());
    System.out.println("A002_PROBE_RESULT=" + new ObjectMapper().writeValueAsString(report));
  }
}
