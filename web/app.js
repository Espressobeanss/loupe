(function () {
  var $ = function (id) { return document.getElementById(id); };
  var crumb = $("crumb");

  function show(screen, label) {
    var screens = document.querySelectorAll(".screen");
    for (var i = 0; i < screens.length; i++) screens[i].classList.remove("on");
    $(screen).classList.add("on");
    if (label) crumb.textContent = label;
  }

  // --- intake chips + confidence ceiling ---
  var CONF = ["provisional", "fair", "strong", "high"];
  function recalc() {
    var s = 1;
    if ($("brief").value.trim().length > 14) s += 1;
    if (document.querySelector("#role .chip.sel")) s += 1;
    s += Math.min(document.querySelectorAll("#sources .chip.sel").length, 2);
    var tier = CONF[Math.min(s, CONF.length - 1)];
    $("tier").textContent = tier;
    $("fill").style.width = Math.min(Math.round((s / 4) * 100), 96) + "%";
  }

  document.querySelectorAll("#s-intake .chip").forEach(function (c) {
    c.addEventListener("click", function () {
      var grp = c.closest(".grp");
      if (grp.classList.contains("single")) {
        grp.querySelectorAll(".chip").forEach(function (x) { if (x !== c) x.classList.remove("sel"); });
      }
      c.classList.toggle("sel");
      recalc();
    });
  });
  $("brief").addEventListener("input", recalc);

  function selectedRole() {
    var el = document.querySelector("#role .chip.sel");
    return el ? el.getAttribute("data-v") : "product";
  }

  // --- fetch + render ---
  function fetchReport(role, depth) {
    return fetch("/api/report?role=" + encodeURIComponent(role) + "&depth=" + encodeURIComponent(depth))
      .then(function (r) { return r.json(); });
  }

  var ROLES = ["founder", "product", "design", "engineering", "ops", "growth"];
  var NUM = ["i.", "ii.", "iii.", "iv."];
  var BARCOLOR = ["#D85A30", "#EF9F27", "#EF9F27"];
  var state = { role: "product", depth: "standard" };

  function renderReport(data) {
    var d = state.depth;
    var stdOpen = d !== "quick";
    var deepOpen = d === "deep";

    var html = "";
    html += '<div class="verdict-row"><div class="v">' +
      '<p class="kicker">The verdict &mdash;</p>' +
      '<p class="claim">' + esc(data.verdict.claim) + "</p></div>" +
      '<span class="stamp">' + esc(data.verdict.confidence) + " confidence</span></div>";

    if (deepOpen) {
      var assume = (data.meta.assumptions && data.meta.assumptions.length) ? data.meta.assumptions.join(", ") : "none";
      html += '<p class="ceiling-note">confidence ceiling: ' + esc(data.meta.ceiling) + " &middot; assumptions: " + esc(assume) + "</p>";
    }

    if (stdOpen) {
      html += '<p class="filed">Filed from ' +
        data.inputs.map(function (x) { return x.count + " " + esc(x.source); }).join(", ") +
        " &mdash; freshest " + esc(data.inputs[0].freshness) + ".</p>";

      html += '<p class="sec">What we saw</p>';
      data.signals.forEach(function (sg, i) {
        html += '<div class="sig"><span class="label">' + esc(sg.theme) + "</span>" +
          '<div class="bar"><i style="width:' + sg.weight + "%;background:" + BARCOLOR[i % 3] + '"></i></div>' +
          '<span class="n">' + sg.count + "</span></div>";
        if (deepOpen) {
          var tags = (sg.sourceRefs || []).map(function (r) { return '<span class="src">' + esc(r) + "</span>"; }).join("");
          html += '<div class="sig-detail">&ldquo;' + esc(sg.quote) + "&rdquo;" + tags + "</div>";
        }
      });

      html += '<p class="sec">From the panel</p>';
      var c = data.critiques[0];
      html += '<div class="crit"><p class="voice">&ldquo;' + esc(c.voice) + "&rdquo;</p>" +
        '<div class="meta"><span class="by">&mdash; the crit, on ' + esc(c.principle) + "</span>" +
        '<span class="sev">severity: ' + esc(c.severity) + "</span></div>";
      if (deepOpen) {
        html += '<div class="crit-detail">Who it hits: ' + esc(c.who) + " &middot; confidence: " + esc(c.confidence) + "</div>";
      }
      html += "</div>";
    }

    // role-switchable next steps
    html += '<div class="role-line"><span class="sec" style="margin:0">So, next &mdash; for</span>' +
      '<div class="role-tabs" id="roles">' +
      ROLES.map(function (r) {
        return '<span class="rtab' + (r === state.role ? " on" : "") + '" data-r="' + r + '">' +
          r.charAt(0).toUpperCase() + r.slice(1) + "</span>";
      }).join("") + "</div></div>";
    html += '<p class="note">Same verdict, same crit &mdash; only the actions below re-aim.</p>';

    html += '<div class="steps">';
    data.nextSteps.forEach(function (st, i) {
      html += '<div class="step ' + st.h + '"><span class="num">' + NUM[i] + "</span>" +
        '<div class="body"><div class="head"><span class="hz ' + st.h + '">' + hzLabel(st.h) + "</span>" +
        '<span class="t">' + esc(st.t) + "</span></div>";
      if (st.handoff) {
        html += '<div class="handoff">&#8627; hand to ' + cap(st.handoff.toRole) + ": " + esc(st.handoff.text) + "</div>";
      }
      html += "</div>";
      if (stdOpen && st.ref) html += '<span class="ref">' + esc(st.ref) + "</span>";
      html += "</div>";
    });
    html += "</div>";

    if (deepOpen) html += '<p class="signoff">looked closely, so you could look once. &mdash; Loupe</p>';
    html += '<div class="restart"><button class="btn small" id="restart">&larr; start over</button></div>';

    $("report-body").innerHTML = html;
    wireReport();
  }

  function wireReport() {
    document.querySelectorAll("#roles .rtab").forEach(function (t) {
      t.addEventListener("click", function () {
        state.role = t.getAttribute("data-r");
        fetchReport(state.role, state.depth).then(renderReport);  // re-runs only translate
      });
    });
    $("restart").addEventListener("click", function () { show("s-intake", "before I look"); });
  }

  // depth tabs (render-time filter over the same object)
  document.querySelectorAll("#depth .tab").forEach(function (t) {
    t.addEventListener("click", function () {
      document.querySelectorAll("#depth .tab").forEach(function (x) { x.classList.remove("on"); });
      t.classList.add("on");
      state.depth = t.getAttribute("data-d");
      $("s-report").setAttribute("data-depth", state.depth);
      fetchReport(state.role, state.depth).then(renderReport);
    });
  });

  // --- the look-closer flow ---
  var MSGS = [
    "reading 47 tickets — a sample, then the counts…",
    "reading the Figma flow by reference…",
    "convening the crit…",
  ];
  $("go").addEventListener("click", function () {
    state.role = selectedRole();
    show("s-load", "looking closely");
    var i = 0;
    var el = $("load-msg");
    var t = setInterval(function () {
      i++;
      if (i < MSGS.length) { el.textContent = MSGS[i]; return; }
      clearInterval(t);
      fetchReport(state.role, state.depth).then(function (data) {
        show("s-report", "the checkout read");
        renderReport(data);
      });
    }, 700);
  });

  // helpers
  function esc(s) { return String(s).replace(/[&<>]/g, function (m) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[m]; }); }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function hzLabel(h) { return h === "week" ? "this week" : h; }

  recalc();
})();
