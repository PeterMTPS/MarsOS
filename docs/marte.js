// MarsOS - relogio marciano do site (mesmo algoritmo Mars24 do comando `sol`)
// Mars clock for the website (same Mars24 algorithm as the `sol` command)
(function () {
  "use strict";

  var EN = (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;
  var T = EN ? {
    titulo: "MarsOS · Mars Clock",
    msd: "Mars Sol Date (MSD)", mtc: "Coordinated Mars Time", ano: "Mars year",
    ls: "Solar longitude (Ls)", estacao: "Season", terra: "Earth (UTC)", local: "local time",
    norte: ["Spring", "Summer", "Autumn", "Winter"], sul: ["Autumn", "Winter", "Spring", "Summer"],
    noNorte: " in the north", noSul: " in the south",
    distancia: "Distance from Earth", sinal: "Signal delay", idaVolta: "round trip", ua: "AU",
    conjuncao: "Solar conjunction: the Sun is between Earth and Mars."
  } : {
    titulo: "MarsOS · Relógio Marciano",
    msd: "Sol marciano (MSD)", mtc: "Hora coordenada (MTC)", ano: "Ano marciano",
    ls: "Longitude solar (Ls)", estacao: "Estação", terra: "Terra (UTC)", local: "hora local",
    norte: ["Primavera", "Verão", "Outono", "Inverno"], sul: ["Outono", "Inverno", "Primavera", "Verão"],
    noNorte: " no norte", noSul: " no sul",
    distancia: "Distância da Terra", sinal: "Atraso do sinal", idaVolta: "ida e volta", ua: "UA",
    conjuncao: "Conjunção solar: o Sol está entre a Terra e Marte."
  };

  var TT_UTC = 69.184;
  var PBS = [
    [0.0071, 2.2353, 49.409], [0.0057, 2.7543, 168.173], [0.0039, 1.1177, 191.837],
    [0.0037, 15.7866, 21.736], [0.0021, 2.1354, 15.704], [0.0020, 2.4694, 95.528],
    [0.0018, 32.8493, 49.095]
  ];
  var LOCAIS = [["Gale (Curiosity)", 137.4417], ["Jezero (Perseverance)", 77.4509], ["Olympus Mons", 226.2]];
  var rad = Math.PI / 180;

  function calcular(ms) {
    var jdTT = 2440587.5 + ms / 86400000 + TT_UTC / 86400;
    var dt = jdTT - 2451545.0;
    var M = ((19.3871 + 0.52402073 * dt) % 360) * rad;
    var alfa = (270.3871 + 0.524038496 * dt) % 360;
    var pbs = 0;
    PBS.forEach(function (p) { pbs += p[0] * Math.cos((0.985626 * dt / p[1] + p[2]) * rad); });
    var eqc = (10.691 + 3e-7 * dt) * Math.sin(M) + 0.623 * Math.sin(2 * M) + 0.050 * Math.sin(3 * M) +
              0.005 * Math.sin(4 * M) + 0.0005 * Math.sin(5 * M) + pbs;
    var ls = ((alfa + eqc) % 360 + 360) % 360;
    var msd = (jdTT - 2405522.0028779) / 1.0274912517;
    var mtc = ((24 * msd) % 24 + 24) % 24;
    var ano = 36 + Math.round(((msd - 52292.88) - (ls / 360) * 668.5921) / 668.5921);
    return { msd: msd, mtc: mtc, ls: ls, ano: ano };
  }

  // Distancia Terra-Marte e atraso do sinal (elementos orbitais do JPL, "Approximate
  // Positions of the Planets", tabela 1) - o mesmo calculo do `sol` no MarsOS.
  var ELEM = {
    terra: [[1.00000261, 0.00000562], [0.01671123, -0.00004392], [-0.00001531, -0.01294668],
            [100.46457166, 35999.37244981], [102.93768193, 0.32327364], [0, 0]],
    marte: [[1.52371034, 0.00001847], [0.09339410, 0.00007882], [1.84969142, -0.00813131],
            [-4.55343205, 19140.30268499], [-23.94362959, 0.44441088], [49.55953891, -0.29257343]]
  };
  function posicao(el, t) {
    var a = el[0][0] + el[0][1] * t, e = el[1][0] + el[1][1] * t, inc = (el[2][0] + el[2][1] * t) * rad;
    var L = el[3][0] + el[3][1] * t, peri = el[4][0] + el[4][1] * t, no = el[5][0] + el[5][1] * t;
    var w = (peri - no) * rad, O = no * rad, M = (((L - peri) % 360) + 360) % 360 * rad;
    var E = M + e * Math.sin(M);
    for (var i = 0; i < 10; i++) { E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E)); }
    var xp = a * (Math.cos(E) - e), yp = a * Math.sqrt(1 - e * e) * Math.sin(E);
    var cw = Math.cos(w), sw = Math.sin(w), cO = Math.cos(O), sO = Math.sin(O), ci = Math.cos(inc), si = Math.sin(inc);
    return [(cw * cO - sw * sO * ci) * xp + (-sw * cO - cw * sO * ci) * yp,
            (cw * sO + sw * cO * ci) * xp + (-sw * sO + cw * cO * ci) * yp,
            (sw * si) * xp + (cw * si) * yp];
  }
  function sinal(ms) {
    var t = (2440587.5 + (ms / 1000 + TT_UTC) / 86400 - 2451545.0) / 36525;
    var p = posicao(ELEM.terra, t), q = posicao(ELEM.marte, t);
    var d = [q[0] - p[0], q[1] - p[1], q[2] - p[2]];
    var ua = Math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
    var r = Math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
    var cosEl = -(p[0] * d[0] + p[1] * d[1] + p[2] * d[2]) / (r * ua);
    var km = ua * 149597870.7;
    return { ua: ua, km: km, seg: km / 299792.458, elong: Math.acos(Math.max(-1, Math.min(1, cosEl))) / rad };
  }
  function duracao(seg) {
    var s = Math.round(seg);
    return Math.floor(s / 60) + " min " + (s % 60 < 10 ? "0" : "") + (s % 60) + " s";
  }

  function hms(h) {
    var s = Math.round((((h % 24) + 24) % 24) * 3600) % 86400;
    function d(n) { return (n < 10 ? "0" : "") + n; }
    return d(Math.floor(s / 3600)) + ":" + d(Math.floor(s % 3600 / 60)) + ":" + d(s % 60);
  }
  function milhar(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, EN ? "," : "."); }
  function dec(x, casas) { var s = x.toFixed(casas); return EN ? s : s.replace(".", ","); }
  function pad(rotulo) { var s = rotulo + " "; while (s.length < 26) s += "."; return s; }

  function atualizar() {
    var agora = Date.now();
    var m = calcular(agora);
    var est = Math.floor(m.ls / 90) % 4;
    var sol = milhar(Math.floor(m.msd));

    var mini = document.getElementById("mini-sol");
    if (mini) {
      mini.innerHTML = "<b>SOL " + sol + "</b><span>MTC " + hms(m.mtc).slice(0, 5) + "</span>";
    }
    var term = document.getElementById("terminal-sol");
    if (term) {
      var a = function (r) { return '  <span class="a">' + pad(r) + "</span> "; };
      var linhas = [
        '<span class="p">astronauta@marte</span>:<span class="h">~</span>$ sol',
        "",
        '  <span class="p">' + T.titulo + "</span>",
        '  <span class="a">────────────────────────────────────────────</span>',
        a(T.msd) + '<span class="h">' + sol + "</span>  (" + dec(m.msd, 4) + ")",
        a(T.mtc) + '<span class="h">' + hms(m.mtc) + "</span>",
        a(T.ano) + m.ano,
        a(T.ls) + dec(m.ls, 1) + "°",
        a(T.estacao) + T.norte[est] + T.noNorte + " · " + T.sul[est] + T.noSul
      ];
      LOCAIS.forEach(function (l) {
        linhas.push(a(l[0]) + hms(m.mtc + l[1] / 15).slice(0, 5) + " (" + T.local + ")");
      });
      linhas.push(a(T.terra) + new Date(agora).toISOString().replace("T", " ").slice(0, 19));
      var sn = sinal(agora);
      linhas.push(a(T.distancia) + milhar(Math.floor(sn.km)) + " km (" + dec(sn.ua, 2) + " " + T.ua + ")");
      linhas.push(a(T.sinal) + '<span class="h">' + duracao(sn.seg) + "</span>  (" + T.idaVolta + ": " + duracao(2 * sn.seg) + ")");
      if (sn.elong < 3) { linhas.push('  <span class="p">' + T.conjuncao + "</span>"); }
      linhas.push("", '<span class="p">astronauta@marte</span>:<span class="h">~</span>$ <span class="cursor"></span>');
      term.innerHTML = linhas.join("\n");
    }
    var relogio = document.getElementById("hora-terra");
    if (relogio) {
      var d = new Date(agora);
      relogio.textContent = (d.getHours() < 10 ? "0" : "") + d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes();
    }
  }

  // som de inicializacao / startup sound
  var botaoSom = document.getElementById("tocar-som");
  if (botaoSom) {
    var audio = new Audio(botaoSom.getAttribute("data-som") || "img/inicio.wav");
    botaoSom.addEventListener("click", function () {
      audio.currentTime = 0;
      audio.play();
    });
  }

  atualizar();
  setInterval(atualizar, 1000);
})();
