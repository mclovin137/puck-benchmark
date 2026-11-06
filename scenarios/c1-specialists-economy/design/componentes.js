/* componentes.js — JS mínimo e opcional do padrão visual (sem dependências, sem build).
   Sem este arquivo, a página continua legível e navegável (progressive enhancement).
   API global: window.Ui = { toast, tema, modo, progresso, carregando, abrirPaleta }. */
(function () {
  "use strict";
  var raiz = document.documentElement;
  var reduzido = function () { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var guardar = function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignora */ } };
  var ler = function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } };
  var contador = 0;
  var uid = function (p) { return p + "-" + (++contador); };

  raiz.classList.add("js-ativo");

  /* ---- Tema e modo (URL > armazenamento > padrão) ---- */
  function transicao(fn) {
    if (document.startViewTransition && !reduzido()) { document.startViewTransition(fn); } else { fn(); }
  }
  function tema(n) {
    if (n === undefined) { return raiz.getAttribute("data-tema") || "1"; }
    transicao(function () { raiz.setAttribute("data-tema", String(n)); });
    guardar("ui-tema", n);
    $$('input[name="tema"]').forEach(function (i) { i.checked = i.value === String(n); });
  }
  function modo(m) { // "auto" | "claro" | "escuro"
    if (m === "auto") { raiz.removeAttribute("data-modo"); } else { transicao(function () { raiz.setAttribute("data-modo", m); }); }
    guardar("ui-modo", m);
    $$(".seletor-modo button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.modo === m)); });
  }
  var params = new URLSearchParams(location.search);
  var t0 = params.get("tema") || ler("ui-tema");
  var m0 = params.get("modo") || ler("ui-modo") || "auto";
  if (t0 && /^[1-5]$/.test(t0)) { raiz.setAttribute("data-tema", t0); }
  if (m0 === "claro" || m0 === "escuro") { raiz.setAttribute("data-modo", m0); }

  /* ---- Toast (aria-live, desfazer em vez de confirmar) ---- */
  function toast(msg, o) {
    o = o || {};
    var area = $(".toasts");
    if (!area) {
      area = document.createElement("div");
      area.className = "toasts";
      area.setAttribute("role", "status");
      area.setAttribute("aria-live", "polite");
      document.body.appendChild(area);
    }
    var el = document.createElement("div");
    el.className = "toast" + (o.tipo ? " toast--" + o.tipo : "");
    var p = document.createElement("p");
    p.className = "toast__msg";
    p.textContent = msg;
    el.appendChild(p);
    function fechar() {
      if (!el.parentNode) { return; }
      el.classList.add("toast--saindo");
      setTimeout(function () { if (el.parentNode) { el.remove(); } }, reduzido() ? 0 : 200);
    }
    if (o.acao) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "btn btn--fantasma btn--pequeno toast__acao";
      b.textContent = o.acao;
      b.addEventListener("click", function () { if (o.aoAcionar) { o.aoAcionar(); } fechar(); });
      el.appendChild(b);
    }
    area.appendChild(el);
    setTimeout(fechar, o.duracao || 5000);
    return fechar;
  }

  /* ---- Botão carregando ---- */
  function carregando(btn, ativo) {
    if (ativo) { btn.setAttribute("aria-busy", "true"); } else { btn.removeAttribute("aria-busy"); }
  }
  $$(".btn").forEach(function (b) {
    if (b.dataset.carregar !== undefined && !$(".btn__girar", b)) {
      var s = document.createElement("span");
      s.className = "btn__girar";
      s.setAttribute("aria-hidden", "true");
      b.insertBefore(s, b.firstChild);
    }
  });
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-carregar]");
    if (!b || b.getAttribute("aria-busy") === "true") { return; }
    carregando(b, true);
    setTimeout(function () { carregando(b, false); toast(b.dataset.carregar || "Pronto!", { tipo: "sucesso" }); }, 1400);
  });

  /* ---- Progresso ---- */
  function progresso(el, v) {
    v = Math.max(0, Math.min(100, v));
    el.style.setProperty("--valor", v);
    var trilho = $('[role="progressbar"]', el);
    if (trilho) { trilho.setAttribute("aria-valuenow", Math.round(v)); }
    var rot = $("[data-valor-texto]", el);
    if (rot) { rot.textContent = Math.round(v) + "%"; }
  }

  /* ---- Validação inline descritiva ---- */
  var MENSAGENS = {
    valueMissing: function (c) { return "Preencha " + (c.dataset.nome || "este campo") + "."; },
    typeMismatch: function (c) { return c.type === "email" ? "Digite um e-mail completo, como nome@empresa.com." : "O formato não é válido."; },
    tooShort: function (c) { return "Use pelo menos " + c.minLength + " caracteres (faltam " + (c.minLength - c.value.length) + ")."; },
    patternMismatch: function (c) { return c.title || "O formato não é válido."; }
  };
  function validarCampo(entrada, forcar) {
    var campo = entrada.closest(".campo");
    if (!campo) { return true; }
    var msg = campo.querySelector(".campo__erro");
    if (!forcar && !entrada.dataset.tocado) { return entrada.checkValidity(); }
    var v = entrada.validity, texto = "";
    if (!v.valid) {
      for (var k in MENSAGENS) { if (v[k]) { texto = MENSAGENS[k](entrada); break; } }
      texto = texto || entrada.validationMessage;
    }
    if (msg) {
      msg.textContent = texto;
      if (!msg.id) { msg.id = uid("erro"); }
    }
    campo.dataset.estado = v.valid ? (entrada.value ? "ok" : "") : "erro";
    entrada.setAttribute("aria-invalid", String(!v.valid));
    var ids = (entrada.getAttribute("aria-describedby") || "").split(" ").filter(function (i) { return i && !i.startsWith("erro-"); });
    if (!v.valid && msg) { ids.push(msg.id); }
    if (ids.length) { entrada.setAttribute("aria-describedby", ids.join(" ")); } else { entrada.removeAttribute("aria-describedby"); }
    return v.valid;
  }
  document.addEventListener("focusout", function (e) {
    if (e.target.matches && e.target.matches(".campo__entrada")) { e.target.dataset.tocado = "1"; validarCampo(e.target); }
  });
  document.addEventListener("input", function (e) {
    if (e.target.matches && e.target.matches(".campo__entrada") && e.target.dataset.tocado) { validarCampo(e.target); }
  });
  $$("form[data-validar]").forEach(function (f) {
    f.noValidate = true;
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var invalidos = $$(".campo__entrada", f).filter(function (i) { i.dataset.tocado = "1"; return !validarCampo(i, true); });
      if (invalidos.length) {
        invalidos[0].focus();
        toast(invalidos.length === 1 ? "Falta corrigir 1 campo." : "Faltam corrigir " + invalidos.length + " campos.", { tipo: "erro" });
        return;
      }
      toast(f.dataset.sucesso || "Salvo.", { tipo: "sucesso", acao: "Desfazer", aoAcionar: function () { toast("Desfeito."); } });
      f.reset();
      $$(".campo", f).forEach(function (c) { c.dataset.estado = ""; });
    });
  });

  /* ---- Modal (<dialog>) ---- */
  document.addEventListener("click", function (e) {
    var abrir = e.target.closest("[data-abrir-modal]");
    if (abrir) { var d = document.getElementById(abrir.dataset.abrirModal); if (d && d.showModal) { d.showModal(); } return; }
    var fechar = e.target.closest("[data-fechar]");
    if (fechar) { var dd = fechar.closest("dialog"); if (dd) { dd.close(fechar.dataset.fechar || ""); } return; }
    if (e.target.tagName === "DIALOG") { e.target.close("cancelar"); } // clique no fundo escurecido
  });

  /* ---- Abas (setas, Home/End; foco no painel não é preso) ---- */
  $$("[data-abas]").forEach(function (raizAbas) {
    var abas = $$('[role="tab"]', raizAbas);
    function ativar(aba, foco) {
      abas.forEach(function (a) {
        var sel = a === aba;
        a.setAttribute("aria-selected", String(sel));
        a.tabIndex = sel ? 0 : -1;
        document.getElementById(a.getAttribute("aria-controls")).hidden = !sel;
      });
      if (foco) { aba.focus(); }
    }
    abas.forEach(function (a, i) {
      a.addEventListener("click", function () { ativar(a); });
      a.addEventListener("keydown", function (e) {
        var j = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: abas.length - 1 }[e.key];
        if (j === undefined) { return; }
        e.preventDefault();
        ativar(abas[(j + abas.length) % abas.length], true);
      });
    });
  });

  /* ---- Navegação lateral responsiva ---- */
  var alternar = $(".nav__alternar"), lateral = $(".nav-lateral");
  if (alternar && lateral) {
    var definir = function (aberta) { lateral.dataset.aberta = String(aberta); alternar.setAttribute("aria-expanded", String(aberta)); };
    alternar.addEventListener("click", function () { definir(lateral.dataset.aberta !== "true"); });
    lateral.addEventListener("click", function (e) { if (e.target.closest("a")) { definir(false); } });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && lateral.dataset.aberta === "true") { definir(false); alternar.focus(); } });
    var links = $$(".nav__link", lateral);
    var alvos = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (en.isIntersecting) {
            links.forEach(function (a) { if (a.getAttribute("href") === "#" + en.target.id) { a.setAttribute("aria-current", "true"); } else { a.removeAttribute("aria-current"); } });
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      alvos.forEach(function (s) { if (s) { obs.observe(s); } });
    }
  }

  /* ---- Command palette (Ctrl/⌘+K): qualquer ação em 1–2 cliques ---- */
  var paleta = $("#paleta");
  function abrirPaleta() { if (paleta && !paleta.open) { paleta.showModal(); montar(""); $(".paleta__busca", paleta).focus(); } }
  var itens = [], ativo = 0;
  function montar(q) {
    var lista = $(".paleta__lista", paleta), vazio = $(".paleta__vazio", paleta);
    var termo = q.trim().toLowerCase();
    itens = $$("[data-comando]").map(function (el) { return { el: el, rotulo: el.dataset.comando, grupo: el.dataset.grupo || "Ações" }; })
      .filter(function (c) { return !termo || (c.rotulo + " " + c.grupo).toLowerCase().indexOf(termo) !== -1; });
    lista.textContent = "";
    itens.forEach(function (c, i) {
      var li = document.createElement("li");
      li.id = "paleta-op-" + i;
      li.className = "paleta__item";
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", "false");
      var a = document.createElement("span"); a.textContent = c.rotulo;
      var g = document.createElement("span"); g.className = "paleta__grupo"; g.textContent = c.grupo;
      li.appendChild(a); li.appendChild(g);
      li.addEventListener("click", function () { executar(i); });
      li.addEventListener("mousemove", function () { marcar(i); });
      lista.appendChild(li);
    });
    vazio.hidden = itens.length > 0;
    marcar(0);
  }
  function marcar(i) {
    ativo = Math.max(0, Math.min(itens.length - 1, i));
    var busca = $(".paleta__busca", paleta);
    $$(".paleta__item", paleta).forEach(function (li, k) { li.setAttribute("aria-selected", String(k === ativo)); });
    var sel = $("#paleta-op-" + ativo);
    if (sel) { busca.setAttribute("aria-activedescendant", sel.id); sel.scrollIntoView({ block: "nearest" }); } else { busca.removeAttribute("aria-activedescendant"); }
  }
  function executar(i) {
    var c = itens[i]; if (!c) { return; }
    paleta.close();
    setTimeout(function () { c.el.click(); if (c.el.tagName === "A" && c.el.hash) { /* navegação nativa pelo clique */ } }, 0);
  }
  if (paleta) {
    $(".paleta__busca", paleta).addEventListener("input", function (e) { montar(e.target.value); });
    paleta.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); marcar(ativo + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); marcar(ativo - 1); }
      else if (e.key === "Enter") { e.preventDefault(); executar(ativo); }
    });
    paleta.addEventListener("click", function (e) { if (e.target === paleta) { paleta.close(); } });
  }
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); if (paleta && paleta.open) { paleta.close(); } else { abrirPaleta(); } }
  });
  $$("[data-abrir-paleta]").forEach(function (b) { b.addEventListener("click", abrirPaleta); });

  /* ---- Stepper curto ---- */
  $$("[data-stepper]").forEach(function (st) {
    var passos = $$(".stepper__passo", st), paineis = $$(".stepper__painel", st), atual = 0;
    function ir(n, foco) {
      atual = n;
      passos.forEach(function (p, i) {
        if (i === n) { p.setAttribute("aria-current", "step"); } else { p.removeAttribute("aria-current"); }
        p.dataset.estado = i < n ? "feito" : "";
      });
      paineis.forEach(function (p, i) { p.hidden = i !== n; });
      if (foco) { var h = $("h3, h4", paineis[n]); if (h) { h.tabIndex = -1; h.focus(); } }
    }
    st.addEventListener("click", function (e) {
      var b = e.target.closest("[data-passo]");
      if (!b) { return; }
      if (b.dataset.passo === "voltar") { ir(Math.max(0, atual - 1), true); return; }
      var invalidos = $$(".campo__entrada", paineis[atual]).filter(function (i) { i.dataset.tocado = "1"; return !validarCampo(i, true); });
      if (invalidos.length) { invalidos[0].focus(); return; }
      if (b.dataset.passo === "concluir") { toast(st.dataset.sucesso || "Concluído!", { tipo: "sucesso" }); ir(0, true); return; }
      ir(Math.min(paineis.length - 1, atual + 1), true);
    });
    ir(0, false);
  });

  /* ---- Seletor de tema/modo ---- */
  $$('input[name="tema"]').forEach(function (i) {
    i.checked = i.value === tema();
    i.addEventListener("change", function () { tema(i.value); });
  });
  $$(".seletor-modo button").forEach(function (b) {
    b.setAttribute("aria-pressed", String(b.dataset.modo === m0));
    b.addEventListener("click", function () { modo(b.dataset.modo); });
  });

  /* ---- Revelar ao rolar ---- */
  var revelar = $$(".revelar");
  if ("IntersectionObserver" in window && !reduzido() && !params.has("capturar")) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("visivel"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    revelar.forEach(function (el, i) { el.style.setProperty("--i", i % 4); io.observe(el); });
  } else {
    revelar.forEach(function (el) { el.classList.add("visivel"); });
  }

  window.Ui = { toast: toast, tema: tema, modo: modo, progresso: progresso, carregando: carregando, abrirPaleta: abrirPaleta };
})();
