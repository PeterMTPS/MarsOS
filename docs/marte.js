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
    noNorte: " in the north", noSul: " in the south"
  } : {
    titulo: "MarsOS · Relógio Marciano",
    msd: "Sol marciano (MSD)", mtc: "Hora coordenada (MTC)", ano: "Ano marciano",
    ls: "Longitude solar (Ls)", estacao: "Estação", terra: "Terra (UTC)", local: "hora local",
    norte: ["Primavera", "Verão", "Outono", "Inverno"], sul: ["Outono", "Inverno", "Primavera", "Verão"],
    noNorte: " no norte", noSul: " no sul"
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
